import re

import pytest
import src.sensortags.parsers.minew_s4_alarm as minew


def test_all_triggered():
    battery = "64"
    door_alarm = "01"
    anti_tamper_alarm = "01"
    history = "01"

    adv_data = f"02010612ff3906a401{battery}{door_alarm}{anti_tamper_alarm}{history}ff0677aa3f23ac3b5a"
    result = re.match(minew.tokens_reg_ex, adv_data, re.VERBOSE)
    assert result, "Reg Ex did not match on adv_data"
    values = minew.process_adv_data(result)
    assert values["battery_level"] == 100
    assert values["alarm_status"] == 1
    assert values["anti_tamper"] == 1
    assert values["history"] == 1


def test_none_triggered():
    battery = "32"
    door_alarm = "00"
    anti_tamper_alarm = "00"
    history = "00"

    adv_data = f"02010612ff3906a401{battery}{door_alarm}{anti_tamper_alarm}{history}ff0677aa3f23ac3b5a"
    result = re.match(minew.tokens_reg_ex, adv_data, re.VERBOSE)
    assert result, "Reg Ex did not match on adv_data"
    values = minew.process_adv_data(result)
    assert values["battery_level"] == 50
    assert values["alarm_status"] == 0
    assert values["anti_tamper"] == 0
    assert values["history"] == 0
