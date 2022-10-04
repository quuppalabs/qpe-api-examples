"""Commonly added arguments for scripts
"""

import argparse
import json
import logging
import os
import pathlib
import time


def add_qpe_base_url_arg(parser) -> None:
    parser.add_argument(
        "--qpe_addr",
        action="store",
        default="http://localhost:8080/qpe",
        help="what url to poll QPE data from",
    )


def add_poll_interval_arg(parser):
    parser.add_argument(
        "--poll_interval",
        action="store",
        default=15.0,
        type=float,
        help="Time in seconds between polling calls to QPE",
    )


def add_id_arg(parser) -> None:
    parser.add_argument(
        "--id",
        action="store",
        default="",
        help="which id to use",
    )


def configure_logging():
    """this function provides a basic logging module initialization"""

    log_path = pathlib.Path("logs")
    if not os.path.exists(log_path):
        os.makedirs(log_path)

    # logfile will be in /logs/<datetime>.log for instance
    log_path = log_path / (time.strftime(r"%Y%m%d-%H%M%S") + ".log")

    log: logging.Logger = logging.getLogger("")
    log.setLevel(logging.DEBUG)

    log_file = logging.FileHandler(log_path)
    log_file.setLevel(logging.DEBUG)
    log_file.setFormatter(logging.Formatter("%(asctime)s:%(levelname)s:%(name)s: %(message)s"))

    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    ch.setFormatter(logging.Formatter("%(asctime)s:%(levelname)s:%(name)s: %(message)s"))

    log.addHandler(log_file)
    log.addHandler(ch)
    log.info("Logging started successfully")


def get_influx_credentials() -> dict:
    with open("keys/keys.json") as json_file:
        keys = json.load(json_file)
        return keys["influx_db_system_monitor"]
