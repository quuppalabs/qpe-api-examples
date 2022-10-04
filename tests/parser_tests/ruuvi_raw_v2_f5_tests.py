import re
from os import truncate

import pytest
import src.sensortags.parsers.ruuvi_raw_v2_f5 as ruuvi


def test_catch_all_valid_data():
    adv_data = "02010611ff99040512fc5394c37c0004fffc040cac364200cdcbb8334c884f"
    result = re.match(ruuvi.tokens_reg_ex, adv_data, re.VERBOSE)
    assert result, "Reg Ex did not match on adv_data"
    values = ruuvi.process_adv_data(result)
    assert values["temperature"] == 24.3
    assert values["pressure"] == 100044
    assert values["humidity"] == 53.49
    assert values["acceleration_x"] == 4
    assert values["acceleration_y"] == -4
    assert values["acceleration_z"] == 1036
    assert round(values["battery"], 3) == 2.977
    assert values["tx_power"] == 4
    assert values["movement_counter"] == 66
    assert values["measurement_sequence_number"] == 205


def test_catch_all_max_value_data():
    adv_data = "02010611ff9904057ffffffefffe7fff7fff7fffffdefefffecbb8334c884f"
    result = re.match(ruuvi.tokens_reg_ex, adv_data, re.VERBOSE)
    assert result, "Reg Ex did not match on adv_data"
    values = ruuvi.process_adv_data(result)
    assert values["temperature"] == 163.835
    assert values["pressure"] == 115534
    assert values["humidity"] == 163.8350
    assert values["acceleration_x"] == 32767
    assert values["acceleration_y"] == 32767
    assert values["acceleration_z"] == 32767
    assert round(values["battery"], 3) == 3.646
    assert values["tx_power"] == 20
    assert values["movement_counter"] == 254
    assert values["measurement_sequence_number"] == 65534


def test_catch_all_min_value_data():
    adv_data = "02010611ff9904058001000000008001800180010000000000cbb8334c884f"
    result = re.match(ruuvi.tokens_reg_ex, adv_data, re.VERBOSE)
    assert result, "Reg Ex did not match on adv_data"
    values = ruuvi.process_adv_data(result)
    assert values["temperature"] == -163.835
    assert values["pressure"] == 50000
    assert values["humidity"] == 0.0
    assert values["acceleration_x"] == -32767
    assert values["acceleration_y"] == -32767
    assert values["acceleration_z"] == -32767
    assert round(values["battery"], 3) == 1.600
    assert values["tx_power"] == -40
    assert values["movement_counter"] == 0
    assert values["measurement_sequence_number"] == 0
