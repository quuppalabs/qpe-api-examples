import re

import pytest
import src.sensortags.parsers.minew_e6 as minew


def test_light():
    light = "01"
    adv_data = f"0201060303e1ff0d16e1ffa10264{light}169aa23f23ac"
    result = re.match(minew.tokens_reg_ex, adv_data, re.VERBOSE)
    assert result, "Reg Ex did not match on adv_data"
    values = minew.process_adv_data(result)
    assert values["light_sensor_value"] == 1


def test_light():
    light = "00"
    adv_data = f"0201060303e1ff0d16e1ffa10264{light}169aa23f23ac"
    result = re.match(minew.tokens_reg_ex, adv_data, re.VERBOSE)
    assert result, "Reg Ex did not match on adv_data"
    values = minew.process_adv_data(result)
    assert values["light_sensor_value"] == 0
