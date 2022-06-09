"""Provides tokenizing and post processing

The S4 is a magnetic door open or closed sensor

Sample Advertising Data:  0x02 0x01 0x06 0x12 0xff 0x39 0x06 0xa4 0x01 0x64 0x01 0x01 0x00 0xff 0x06 0x77 0xaa 0x3f 0x23 0xac 0x3b 0x5a
                          0x02 0x01 0x06 0x15 0xff 0x39 0x06 0xa4 0x00 0x01 0x00 0x02 0x00 0x02 0x01 0x00 0x02 0x06 0x77 0xaa 0x3f 0x23 0xac 0xd5 0x46
02010612ff3906a40164010100ff0677aa3f23ac3b5a
"""

import re

import helpers.tools as tools


tokens_reg_ex = r"""0201060303e1ff[0-9a-z]{2}16e1ffa101
                ([0-9a-z]{2})   # Battery level 0x64 Battery level is 100%
                ([0-9a-z]{4})   # Temperature 0x1147 (8.8 fixed-point)17.28°C
                ([0-9a-z]{4})   # Humidity 0x35D7 (8.8 fixed-point) 53.84%
                ([0-9a-z]{12})  # little endian MAC address
                """


def process_adv_data(result: re.Match) -> dict:
    # "_" in name causes this to be ignored when sending to influx DB
    return {
        "battery_level": int(result.group(1), 16),
        "temperature": tools.float_from_8_8(result.group(2)),
        "humidity": tools.float_from_8_8(result.group(3)),
        "_little_endian_mac": str(result.group(4)),
    }
