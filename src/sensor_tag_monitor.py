import argparse
import logging
import time
import requests

from helpers.urls import QpeUrlCompendium
from src.helpers.influxdata import GatewayTag, InfluxPoint
import src.helpers.startup as startup
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
from influxdb_client.rest import ApiException


def post_point_to_influx(point):
    log = logging.getLogger("SensorMon")

    influx_creds = startup.get_influx_credentials()
    influx = InfluxDBClient(
        url=influx_creds["url"], token=influx_creds["token"], org=influx_creds["org"]
    )
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

    ## init resources ##
    log = logging.getLogger("SensorMon")
    qpe_urls = QpeUrlCompendium(qpe_base_url)

    ## collect data ##
    log.info("Requesting tag data from QPE...")
    res = requests.get(qpe_urls.get_tag_data_all_items)
    if res.status_code == 200:  # check request success
        raw_data = res.json()
        if raw_data["code"] == 0:  # check QPE response
            gateway_data = [  # filter out tags without gateway data
                tag for tag in raw_data["tags"] if tag["advertisingDataPayload"] != None
            ]
            log.info(f"Got data from QPE")
            log.debug(f"Data:  {gateway_data}")

        elif raw_data["code"] == 11:  # qpe not in track mode
            log.warning("QPE not in track mode, no data acquisition possible")
        else:
            gateway_data = None
            log.error(
                f'Expected QPE code 0, got: {gateway_data["code"]} ... no data received'
            )
    else:
        gateway_data = None
        log.error(f"Expected response code 200, got: {res.code} ... no data received")

    if gateway_data:
        gateway_tags = [GatewayTag.from_any_dict(tag) for tag in gateway_data]
        return gateway_tags
    else:
        log.warning("No tags with gateway data were found")
        return []


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Monitor QPE Resources")
    startup.add_qpe_base_url_arg(parser)
    startup.add_poll_interval_arg(parser)
    startup.add_id_arg(parser)
    args = parser.parse_args()
    startup.configure_logging()
    log: logging.Logger = logging.getLogger("SensorMon")
    log.info(
        f"Started with QPE base url: {args.qpe_addr} and polling every {args.poll_interval} seconds"
    )
    while True:
        pass
    time.sleep(args.poll_interval)
