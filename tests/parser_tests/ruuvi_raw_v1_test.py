import re

import pytest
import src.sensortags.parsers.ruuvi_raw_v1 as ruuvi


def test_negative_temperature():
    temp = "8001"
    adv_data = f"02010611ff99040365{temp}c71effcafff404050b71"
    result = re.match(ruuvi.tokens_reg_ex, adv_data, re.VERBOSE)
    assert result, "Reg Ex did not match on adv_data"
    values = ruuvi.process_adv_data(result)
    assert values["temperature"] == -0.01


def test_negative_temperature_2():
    temp = "8145"
    adv_data = f"02010611ff99040365{temp}c71effcafff404050b71"
    result = re.match(ruuvi.tokens_reg_ex, adv_data, re.VERBOSE)
    assert result, "Reg Ex did not match on adv_data"
    values = ruuvi.process_adv_data(result)
    assert values["temperature"] == -1.69


def test_positive_temperature():
    temp = "0145"
    adv_data = f"02010611ff99040365{temp}c71effcafff404050b71"
    result = re.match(ruuvi.tokens_reg_ex, adv_data, re.VERBOSE)
    assert result, "Reg Ex did not match on adv_data"
    values = ruuvi.process_adv_data(result)
    assert values["temperature"] == 1.69


def test_humidity_0():
    humidity = "00"
    adv_data = f"02010611ff990403{humidity}0145c71effcafff404050b71"
    result = re.match(ruuvi.tokens_reg_ex, adv_data, re.VERBOSE)
    assert result, "Reg Ex did not match on adv_data"
    values = ruuvi.process_adv_data(result)
    assert values["humidity"] == 0.0


def test_humidity_50():
    humidity = "80"
    adv_data = f"02010611ff990403{humidity}0145c71effcafff404050b71"
    result = re.match(ruuvi.tokens_reg_ex, adv_data, re.VERBOSE)
    assert result, "Reg Ex did not match on adv_data"
    values = ruuvi.process_adv_data(result)
    assert values["humidity"] == 64.0


def test_humidity_100():
    humidity = "c8"
    adv_data = f"02010611ff990403{humidity}0145c71effcafff404050b71"
    result = re.match(ruuvi.tokens_reg_ex, adv_data, re.VERBOSE)
    assert result, "Reg Ex did not match on adv_data"
    values = ruuvi.process_adv_data(result)
    assert values["humidity"] == 100.0


def test_negative_acceleration_values():
    accel = "fc18"
    adv_data = f"02010611ff990403c80145c71e{accel}{accel}{accel}0b71"
    result = re.match(ruuvi.tokens_reg_ex, adv_data, re.VERBOSE)
    assert result, "Reg Ex did not match on adv_data"
    values = ruuvi.process_adv_data(result)
    assert values["acceleration_x"] == -1000.0


def test_positive_acceleration_values():
    accel = "03e8"
    adv_data = f"02010611ff990403c80145c71e{accel}{accel}{accel}0b71"
    result = re.match(ruuvi.tokens_reg_ex, adv_data, re.VERBOSE)
    assert result, "Reg Ex did not match on adv_data"
    values = ruuvi.process_adv_data(result)
    assert values["acceleration_x"] == 1000.0


def test_pressure_values_0():
    pressure = "0000"
    adv_data = f"02010611ff990403c80145{pressure}0000000000000b71"
    result = re.match(ruuvi.tokens_reg_ex, adv_data, re.VERBOSE)
    assert result, "Reg Ex did not match on adv_data"
    values = ruuvi.process_adv_data(result)
    assert values["pressure"] == 50000


def test_pressure_values_mid():
    pressure = "c87d"
    adv_data = f"02010611ff990403c80145{pressure}0000000000000b71"
    result = re.match(ruuvi.tokens_reg_ex, adv_data, re.VERBOSE)
    assert result, "Reg Ex did not match on adv_data"
    values = ruuvi.process_adv_data(result)
    assert values["pressure"] == 101325


def test_pressure_values_max():
    pressure = "ffff"
    adv_data = f"02010611ff990403c80145{pressure}0000000000000b71"
    result = re.match(ruuvi.tokens_reg_ex, adv_data, re.VERBOSE)
    assert result, "Reg Ex did not match on adv_data"
    values = ruuvi.process_adv_data(result)
    assert values["pressure"] == 115535


def test_catch_all_valid_data():
    adv_data = "02010611ff990403291a1ece1efc18f94202ca0b53"
    result = re.match(ruuvi.tokens_reg_ex, adv_data, re.VERBOSE)
    assert result, "Reg Ex did not match on adv_data"
    values = ruuvi.process_adv_data(result)
    assert values["temperature"] == 26.3
    assert values["pressure"] == 102766
    assert values["humidity"] == 20.5
    assert values["acceleration_x"] == -1000
    assert values["acceleration_y"] == -1726
    assert values["acceleration_z"] == 714
    assert values["battery"] == 2.899
