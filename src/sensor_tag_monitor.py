#!/usr/bin/env python3.10
# Python 3.10.0
"""
This script functions as an example of how to monitor a tags with advertising data 
collected via the QPE Gateway feature. It provides some library boiler plate
to aid in rapid development of scripts to extract application specific data along
with a base example.
The script expects a keys.json file to be available, which is
described further on in the script for use with Influx DB.

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

This does not check if collected data is stale before posting

"""
__author__ = "Quuppa"

import argparse
import logging
import pprint
import time

import requests
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
from influxdb_client.rest import ApiException

import helpers.startup as startup
from helpers.urls import QpeUrlCompendium
from sensortags.sensordata import GatewayTag, InfluxPoint


def post_point_to_influx(point: dict):
    """a function to handle posting point dicts to
    influx db and potential exceptions. If the post to
    influx does not work, data is still captured in the log file

    Args:
        point (dict): The influx point formatted dict to send
    """
    log = logging.getLogger("SensorMon")

    ################# setup for influx ##########
    influx_creds = startup.get_influx_credentials()
    influx = InfluxDBClient(url=influx_creds["url"], token=influx_creds["token"], org=influx_creds["org"])
    write_api = influx.write_api(write_options=SYNCHRONOUS)

    ################# post data #################
    log.info("Writing data to influx cloud...")
    try:
        write_api.write(
            bucket=influx_creds["bucket"],
            org=influx_creds["org"],
            record=point,
        )
        log.info("...Completed")
    except ApiException:
        log.error("Could not post to Influx Cloud!!!!")


def get_sensors_values(qpe_base_url: str) -> list[GatewayTag]:
    """uses the getTagData QPE endpoint with format ALL_ITEMS
    to check for tags that have associated advertising data
    captured by a gateway locator

    Args:
        qpe_base_url (str): The QPE instance to poll

    Returns:
        list[GatewayTag]: the list of GatewayTag class instances representing the
        sensor tags collected with valid adv data
    """
    ## init resources ##
    log = logging.getLogger("SensorMon")
    qpe_urls = QpeUrlCompendium(qpe_base_url)

    ## collect data ##
    log.info("Requesting tag data from QPE...")
    base_res = requests.get(qpe_urls.get_tag_data_all_items)
    if base_res.status_code == 200:  # check request success
        qpe_res = base_res.json()
        if qpe_res["code"] == "0":  # check QPE response
            gateway_data = [  # filter out tags without gateway data
                tag for tag in qpe_res["tags"] if tag["advertisingDataPayload"] != None
            ]
            # log.info(f"Got data from QPE: {gateway_data}")

        elif qpe_res["code"] == 11:  # qpe not in track mode
            log.warning("QPE not in track mode, no data acquisition possible")
        else:
            gateway_data = None
            log.error(f'Expected QPE code 0, got: {qpe_res["code"]} ... no data received')
    else:
        gateway_data = None
        log.error(f"Expected response code 200, got: {base_res.code} ... no data received")

    if gateway_data:  # if valid data was gathered attempt to convert to GatewayTags
        gateway_tags = [GatewayTag.from_any_dict(tag) for tag in gateway_data]
        log.debug(f"GatewayTags: {gateway_tags}")
        return gateway_tags
    else:
        log.warning("No tags with gateway data were found")
        return []


if __name__ == "__main__":
    ################# Config and Resource Init #################

    parser = argparse.ArgumentParser(description="Monitor QPE Resources")
    startup.add_qpe_base_url_arg(parser)
    startup.add_poll_interval_arg(parser)
    startup.add_id_arg(parser)
    args = parser.parse_args()

    startup.configure_logging()
    log: logging.Logger = logging.getLogger("SensorMon")

    log.info(f"Started with QPE base url: {args.qpe_addr} and polling every {args.poll_interval} seconds")

    tag_packet_types = {
        "ac233fa29a16": "minew_e6",
        # "ac233fab8231": "minew_s1",
    }

    while True:
        ################# get data and process it #################
        tags = get_sensors_values(args.qpe_addr)
        for tag in tags:
            if tag.tokenize_data(tag_packet_types.get(tag.tagId)):  # if tag was successfully processed
                influx_dict = None  # default incase tag is parsed but not posted

                # if tag.device_type == "minew_e6":  # Influx bucket specific formatting
                influx_dict = tag.as_influx_point_dict(
                    # make the tagId an Influx tag and do not collect
                    # little_endian_mac as a field value
                    tag_keys=["tagId", "advertisingDataPayloadLocatorId"],
                )
                # else:#any tags that are not formatted specially
                #     influx_dict = tag.as_influx_point_dict()

                if influx_dict:
                    log.info(f"Collected sensor data: {influx_dict}")
                    post_point_to_influx(influx_dict)

            else:
                log.warning(f"No parser found for tag: {tag}")

        time.sleep(args.poll_interval)
