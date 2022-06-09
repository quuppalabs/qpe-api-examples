"""Provides tokenizing and post processing

The S1 is a temperature and humidity sensor

Sample Advertising Data:  0x02 0x01 0x06 0x03 0x03 0xe1 0xff 0x10 0x16 0xe1 0xff 0xa1 0x01 0x64 0x1a 0xfd 0x2f 0x94 0x31 0x82 0xab 0x3f 0x23 0xac
0201060303e1ff1016e1ffa101641afd2f943182ab3f23ac
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
