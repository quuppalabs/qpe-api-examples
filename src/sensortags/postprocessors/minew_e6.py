from re import Match


def process_adv_data(result: Match, tokenizer: dict) -> dict:
    return {
        "light_sensor_value": int(result.group(1), 16),
        "little_endian_mac": str(result.group(2)),
    }
