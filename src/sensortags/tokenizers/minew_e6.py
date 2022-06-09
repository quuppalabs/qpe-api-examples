"""Provides tokenizing and post processing

The E6 is a light sensor, the light sensor group will be 00 for dark 
and 01 for light

Sample Advertising Data: 0x02 0x01 0x06 0x03 0x03 0xe1 0xff 0x0d 0x16 0xe1 0xff 0xa1 0x02 0x64 0x00 0x16 0x9a 0xa2 0x3f 0x23 0xac
0201060303e1ff0d16e1ffa1026400169aa23f23ac
"""

import re


tokens_reg_ex = r"""0201060303e1ff[0-9a-z]{2}16e1ffa10264
                ([0-1]{2}) # detected light value
                ([0-9a-z]{12}) # little endian MAC address
                """


def process_adv_data(result: re.Match) -> dict:
    # "_" in name causes this to be ignored when sending to influx DB
    return {
        "light_sensor_value": int(result.group(1), 16),
        "_little_endian_mac": str(result.group(2)),
    }
