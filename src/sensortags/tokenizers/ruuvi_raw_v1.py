"""Provides tokenizing and post processing

The S1 is a temperature and humidity sensor

Sample Advertising Data: 0x02 0x01 0x06 0x11 0xff 0x99 0x04 0x03 0x7e 0x05 0x2f 0xc8 0x40 0xff 0xd2 0xff 0xfa 0x04 0x06 0x0b 0x65
02010611ff9904037e052fc840ffd2fffa04060b65
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
([0-9a-z]{4}) # Battery (millivolts)
"""


def process_adv_data(result: re.Match) -> dict:
    # "_" in name causes this to be ignored when sending to influx DB
    return {
        "humidity": int(result.group(1), 16) * 0.5,
        "temperature": float(tools.hex_string_to_signed_int(result.group(2), 8))
        + int(result.group(3), 16) / 100.0,
        "pressure": int(result.group(4), 16) + 50000,
        "acceleration_x": tools.hex_string_to_signed_int(result.group(5), 16),
        "acceleration_y": tools.hex_string_to_signed_int(result.group(6), 16),
        "acceleration_z": tools.hex_string_to_signed_int(result.group(7), 16),
        "battery": int(result.group(8), 16) * 0.001,
    }
