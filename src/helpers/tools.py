def float_from_8_8(hex_bytes: str) -> float:
    """converts 2 hex bytes in 8.8 notation to a float

    0x11 0x47 -> float_from_8_8("1147") -> return 17.28
    """

    return float(int(hex_bytes[0:2], 16)) + (float(int(hex_bytes[2::], 16)) / 256.0)


def ruuvi_hex_to_signed_float(msb: str, lsb: str, bits=8) -> float:
    msb_int = int(msb, 16)
    lsb_int = float(int(lsb, 16) / 100.0)

    if msb_int & (1 << (bits - 1)):
        msb_int = msb_int & ~(1 << (bits - 1))
        return -(float(msb_int) + lsb_int)

    return float(msb_int) + lsb_int


def hex_string_to_signed_int(hexstr: str, bits: int) -> int:
    value = int(hexstr, 16)
    if value & (1 << (bits - 1)):
        value -= 1 << bits
    return value


def hex_string_to_2s_comp_signed_int(hexstr: str, bits: int) -> int:
    value = int(hexstr, 16)
    if value & (1 << (bits - 1)):
        value -= 1 << bits
    return value
