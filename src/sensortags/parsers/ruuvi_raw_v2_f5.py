"""Provides tokenizing and post processing

The Ruuvi tags have several different sensors and data formats.
Note: the docs say

Sample sensor data Data: 
0201061bff99040513c948ebc2180028ffd003f8aa16399f44f0a7f689bb59

Exact description can be found at:
https://github.com/ruuvi/ruuvi-sensor-protocols/blob/master/dataformat_05.md
"""

import re

import helpers.tools as tools

tokens_reg_ex = r"""0201[0-9a-z]{2}[0-9a-z]{2}ff990405
([0-9a-z]{4}) # Temperature in 0.005 degrees
([0-9a-z]{4}) # Humidity (16bit unsigned) in 0.0025% (0-163.83% range, though realistically 0-100%)
([0-9a-z]{4}) # Pressure (16bit unsigned) in 1 Pa units, with offset of -50 000 Pa
([0-9a-z]{4}) # Acceleration-X (Most Significant Byte first) milli-g
([0-9a-z]{4}) # Acceleration-Y (Most Significant Byte first) milli-g
([0-9a-z]{4}) # Acceleration-Z (Most Significant Byte first) milli-g
([0-9a-z]{4}) # Power info V and dBm
([0-9a-z]{2}) # Movement counter (8 bit unsigned), incremented by motion detection interrupts from accelerometer
([0-9a-z]{4}) # Measurement sequence number
([0-9a-z]{12}) # MAC address
"""


def process_adv_data(result: re.Match) -> dict:
    # "_" in name causes this to be ignored when sending to influx DB
    return {
        "temperature": int(tools.hex_string_to_2s_comp_signed_int((result.group(1)), 16)) * 0.005,
        "humidity": int(result.group(2), 16) * 0.0025,
        "pressure": int(result.group(3), 16) + 50000,
        "acceleration_x": tools.hex_string_to_2s_comp_signed_int(result.group(4), 16),
        "acceleration_y": tools.hex_string_to_2s_comp_signed_int(result.group(5), 16),
        "acceleration_z": tools.hex_string_to_2s_comp_signed_int(result.group(6), 16),
        "battery": (int(result.group(7), 16) >> 5) * 0.001 + 1.6,
        "tx_power": (int(result.group(7), 16) & 0b11111) * 2 - 40,
        "movement_counter": int(result.group(8), 16),
        "measurement_sequence_number": int(result.group(9), 16),
    }
