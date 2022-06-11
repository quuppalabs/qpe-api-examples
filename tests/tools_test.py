import src.helpers.tools as t


def test_8_8():
    assert t.float_from_8_8("ff80") == 255.5


def test_hex_to_signed_int_positive():
    assert t.hex_string_to_signed_int("0fff", 32) == 4095


def test_hex_to_signed_int_negative():
    assert t.hex_string_to_signed_int("ff", 8) == -1
