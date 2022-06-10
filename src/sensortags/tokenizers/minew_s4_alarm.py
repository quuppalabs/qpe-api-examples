"""Provides tokenizing and post processing

The S4 is a magnetic door open or closed sensor

Sample Advertising Data:  0x02 0x01 0x06 0x12 0xff 0x39 0x06 0xa4 0x01 0x64 0x01 0x01 0x00 0xff 0x06 0x77 0xaa 0x3f 0x23 0xac 0x3b 0x5a

02010612ff3906a40164010100ff0677aa3f23ac3b5a
"""

import re


tokens_reg_ex = r"""02010612ff3906a401
([0-9a-z]{2})   # Battery level 0x64 Battery level is 100%
([0-1]{2})      # Door magnets alarm status 0x00: off status; 0x01: on status
([0-1]{2})      # Anti disassembly alarm status 0x00: off status; 0x01: on status
([0-1]{2})      # Alarm trigger sign 0x00: historical trigger; 0x01: current trigger
ff
([0-9a-z]{12})  # little endian MAC address
[0-9a-z]{4}     # 2 random ints
"""


def process_adv_data(result: re.Match) -> dict:
    # "_" in name causes this to be ignored when sending to influx DB
    return {
        "battery_level": int(result.group(1), 16),
        "alarm_status": int(result.group(2)),
        "anti_tamper": int(result.group(3)),
        "history": int(result.group(3)),
        "_little_endian_mac": str(result.group(5)),
    }
