"""Provides tokenizing and post processing

The Ruuvi tags have several different sensors and data formats.

Sample sensor data Data: 
03291A1ECE1EFC18F94202CA0B53

Exact description can be found at:
https://github.com/ruuvi/ruuvi-sensor-protocols/blob/master/dataformat_03.md
"""

import re

import helpers.tools as tools

tokens_reg_ex = r"""0201[0-9a-z]{2}[0-9a-z]{2}ff990403
([0-9a-z]{2}) # Humidity
([0-9a-z]{2}) # Temperature signed integer portion (-127 to 127)
([0-9a-z]{2}) # Temperature fractional portion
([0-9a-z]{4}) # Pressure 0=50000Pa 65536=115536Pa
([0-9a-z]{4}) # Acceleration -  MSB first
([0-9a-z]{4}) # Acceleration -  MSB first
([0-9a-z]{4}) # Acceleration -  MSB first
([0-9a-z]{4}) # Battery (volts)
"""


def process_adv_data(result: re.Match) -> dict:
    # "_" in name causes this to be ignored when sending to influx DB
    return {
        "humidity": int(result.group(1), 16) * 0.5,
        "temperature": float(tools.ruuvi_hex_to_signed_float(result.group(2), result.group(3))),
        "pressure": int(result.group(4), 16) + 50000,
        "acceleration_x": tools.hex_string_to_2s_comp_signed_int(result.group(5), 16),
        "acceleration_y": tools.hex_string_to_2s_comp_signed_int(result.group(6), 16),
        "acceleration_z": tools.hex_string_to_2s_comp_signed_int(result.group(7), 16),
        "battery": int(result.group(8), 16) * 0.001,
    }
