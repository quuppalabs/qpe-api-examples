def float_from_8_8(hex_bytes: str) -> float:
    """converts 2 hex bytes in 8.8 notation to a float

    0x11 0x47 -> float_from_8_8("1147") -> return 17.28
    """

    return float(int(hex_bytes[0:2], 16)) + (float(int(hex_bytes[2::], 16)) / 256.0)


def hex_string_to_signed_int(hexstr, bits):
    value = int(hexstr, 16)
    if value & (1 << (bits - 1)):
        value -= 1 << bits
    return value
