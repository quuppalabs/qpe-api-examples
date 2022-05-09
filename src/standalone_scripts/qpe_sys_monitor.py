#!/usr/bin/env python3.10
# Python 3.10.0
"""
The process here is written to be understood, not to be as 'pythonic' as possible.

This script functions as an example of how to monitor a QPE and its basic
performance remotely. The script expects a keys.json file to be available, which is
described further on in the script.

The general process is as follows:
- Setup 
    - Logging
    - URLs
    - Credentials
    - Handle CL args
- Request data from QPE
- Parse Data
- Post data to influx_db
    - https://cloud2.influxdata.com/signup
    - There is no particular reason Influx_DB has to be the cloud endpoint

"""


__author__ = "Quuppa"
import argparse
import json
import logging
import os
import pathlib
import time
import requests

import influxdb_client
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS


################# setup #################
## log initialization ##
# python boiler plate to setup logging
# to console and a file
log_path = pathlib.Path("logs")
if not os.path.exists(log_path):  # check/create log folder
    os.makedirs(log_path)
# logfile will be in /logs/<datetime>.log for instance
log_path = log_path / (time.strftime(r"%Y%m%d-%H%M%S") + ".log")

log: logging.Logger = logging.getLogger("qpe_mon")
log.setLevel(logging.DEBUG)

log_file = logging.FileHandler(log_path)
log_file.setLevel(logging.DEBUG)
log_file.setFormatter(logging.Formatter("%(asctime)s:%(levelname)s: %(message)s"))

# do not log debug data to console
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)

log.addHandler(log_file)
log.addHandler(ch)
log.info("Logging started successfully")


## get args ##
parser = argparse.ArgumentParser(description="Monitor QPE Resources")
parser.add_argument(
    "--qpe_addr",
    action="store",
    default="http://localhost:8080/qpe",
    help="what base url to poll QPE data from",
)
parser.add_argument(
    "--poll_interval",
    action="store",
    default=15.0,
    type=float,
    help="Time in seconds between polling calls to QPE (minimum 3 sec)",
)

args = parser.parse_args()
args.poll_interval = max(3.0, args.poll_interval)  # poll no faster than 3 seconds
log.info(
    f"Started with QPE base url: {args.qpe_addr} and polling every {args.poll_interval} seconds"
)

## init resources ##
qpeinfo_url = "/".join([args.qpe_addr, "getPEInfo"])

# get credentials for influx_db
##keys.json looks like:
# {
#     "influx_db_system_monitor": {
#         "token": "your token",
#         "org": "your org",
#         "url": "https://eu-central-1-1.aws.cloud2.influxdata.com",
#         "bucket": "SystemMonitor"
#     }
# }
with open("keys/keys.json") as json_file:
    keys = json.load(json_file)
    influx_creds = keys["influx_db_system_monitor"]
    log.info("Loaded influx credentials")
    log.info(f'url: {influx_creds["url"]}')
    log.info(f'org: {influx_creds["org"]}')
    log.info(f'bucket: {influx_creds["bucket"]}')


influx = influxdb_client.InfluxDBClient(
    url=influx_creds["url"], token=influx_creds["token"], org=influx_creds["org"]
)
write_api = influx.write_api(write_options=SYNCHRONOUS)

################# long term actions #################
while True:
    ## collect data ##
    log.info("Requesting info from QPE...")
    res = requests.get(qpeinfo_url)
    if res.status_code == 200:  # check request success 200: Success
        raw_data = res.json()
        if raw_data["code"] == 0:  # check QPE response 0: Ok
            log.debug(raw_data)
            # according to the QPE API docs the response JSON object
            # contains a few fields, of interest here is the "positioningEngine" field
            data = raw_data["positioningEngine"]
            log.info(f"Got data from QPE: {data}")
        else:
            data = None
            log.error(f'Expected QPE code 0, got: {data["code"]} ... no data received')
    else:
        data = None
        log.error(f"Expected response code 200, got: {res.code} ... no data received")

    if data:
        influx_point = Point.from_dict(  # this dict structure can be found in the influx_db docs
            {
                "measurement": data[
                    "projectName"
                ],  # functions as a groupby effectively
                "fields": {  # fields of interest selected here
                    "cpuLoad": data["cpuLoad"],
                    "issues": len(data["issues"]),
                    "memoryAllocated": data["memoryAllocated"] / 1024,
                    "memoryFree": data["memoryFree"] / 1024,
                    "percentMemoryUsed": data["memoryUsed"] / data["memoryMax"],
                    "packetsPerSecond": data["packetsPerSecond"],
                    "running": data["running"],
                    "udpRx": data["udpRx"],
                    "udpTx": data["udpTx"],
                    # note if additional processing is required it could readily be done
                    # like the following:
                    # "someField": data_processing_func(data["some_key"])
                },
            }
        )
        ################# post data #################
        log.info("Writing data to influx cloud...")
        try:
            write_api.write(
                bucket=influx_creds["bucket"],
                org=influx_creds["org"],
                record=influx_point,
            )
            log.info("Writing data to influx cloud: Completed")
        except influxdb_client.rest.ApiException:
            log.error("Could not post to Influx Cloud!!!!")

    ################# end loop #################
    log.info(f"Sleeping for {args.poll_interval}s")
    time.sleep(args.poll_interval)


################# clean up #################
