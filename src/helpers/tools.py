def float_from_8_8(hex_bytes: str) -> float:
    """converts 2 hex bytes in 8.8 notation to a float

    0x11 0x47 -> float_from_8_8("1147") -> return 17.28

    Args:
        hex_bytes (str): the 2 hex bytes in 8.8 notation

    Returns:
        float: the float value
    """

    return float(int(hex_bytes[0:2], 16)) + (float(int(hex_bytes[2::], 16)) / 256.0)


def ruuvi_hex_to_signed_float(msb: str, lsb: str, bits=8) -> float:
    """Converts 2 hex bytes in ruuvi's 8.8 notation to a float

    it differs from standard in that decimal portion divisor is 100 not 256

    Args:
        msb (str): most significant byte
        lsb (str): least significant byte
        bits (int, optional): how many bits are in use. Defaults to 8.

    Returns:
        float: the float value
    """
    msb_int = int(msb, 16)
    lsb_int = float(int(lsb, 16) / 100.0)

    if msb_int & (1 << (bits - 1)):
        msb_int &= ~(1 << (bits - 1))
        return -(float(msb_int) + lsb_int)

    return float(msb_int) + lsb_int


def hex_string_to_2s_comp_signed_int(hexstr: str, bits: int) -> int:
    """converts a hex string to a signed int using 2's complement

    Args:
        hexstr (str): the hex string
        bits (int): number of bits in use

    Returns:
        int: the int value
    """
    value = int(hexstr, 16)
    if value & (1 << (bits - 1)):
        value -= 1 << bits
    return value
