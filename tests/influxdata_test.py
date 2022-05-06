from pprint import pprint
import src.helpers.influxdata as influx
from pprint import pprint


def test_non_public_attr():
    tag = influx.GatewayTag("gtag", "0xff 0x12", 5, 10, "locid", "somelocator")
    pprint(tag.as_influx_point_dict())

    assert False
