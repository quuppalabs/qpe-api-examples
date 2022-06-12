import src.sensortags.tokenizers.ruuvi_raw_v1 as ruuvi
import re
import pytest


def test_negative_temperature():
    adv_data = "02010611ff990403658001c71effcafff404050b71"
    result = re.match(ruuvi.tokens_reg_ex, adv_data, re.VERBOSE)
    assert result, "Reg Ex did not match on adv_data"
    values = ruuvi.process_adv_data(result)
    assert values["temperature"] == -0.01


def test_negative_temperature_2():
    adv_data = "02010611ff990403658145c71effcafff404050b71"
    result = re.match(ruuvi.tokens_reg_ex, adv_data, re.VERBOSE)
    assert result, "Reg Ex did not match on adv_data"
    values = ruuvi.process_adv_data(result)
    assert values["temperature"] == -1.69


def test_positive_temperature():
    adv_data = "02010611ff990403650145c71effcafff404050b71"
    result = re.match(ruuvi.tokens_reg_ex, adv_data, re.VERBOSE)
    assert result, "Reg Ex did not match on adv_data"
    values = ruuvi.process_adv_data(result)
    assert values["temperature"] == 1.69
