import re

import pytest
import src.sensortags.parsers.minew_s1 as minew

# 0201060303e1ff1016e1ffa101641afd2f943182ab3f23ac
# 0201060303e1ff1216e1ffa10364000affe200f83182ab3f23ac

# 0201060303e1ff1016e1ffa101640a304c593182ab3f23ac
# {'battery_level': 100, 'temperature': 10.1875, 'humidity': 76.34765625}}


def test_real_input():
    """Test real input from a sensor"""
    result = re.match(minew.tokens_reg_ex, "0201060303e1ff1016e1ffa101640a304c593182ab3f23ac", re.VERBOSE)
    assert result, "Reg Ex did not match on advertising data"
    values = minew.process_adv_data(result)

    assert values["battery_level"] == 100
    assert values["temperature"] == 10.1875
    assert values["humidity"] == 76.34765625


def test_bad_real_input():
    """Test real input from a different sensor in the same family sensor"""
    result = re.match(minew.tokens_reg_ex, "02010612ff3906a40164010100ff0677aa3f23ac3b5a", re.VERBOSE)
    assert not result, "Reg Ex did matched on advertising data"
