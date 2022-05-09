from pprint import pprint
import src.sensortags.sensordata as sensor
from pprint import pprint


def test_non_public_attr():
    tag = sensor.GatewayTag("tag_id", "0xff 0x12", 5, 10, "locid", "somelocator")
    setattr(tag, "_nonpub", "this should not be in influx point dict")
    point_dict = tag.as_influx_point_dict()

    assert "_nonpub" not in point_dict["fields"]


def test_public_attr():
    tag = sensor.GatewayTag("gtag", "0xff 0x12", 5, 10, "locid", "somelocator")
    setattr(tag, "pub", "this should be in influx point dict")
    point_dict = tag.as_influx_point_dict()

    assert "pub" in point_dict["fields"]


def test_as_influx_point_dict():
    tag = sensor.GatewayTag("gtag", "0xff 0x12", 5, 10, "locid", "somelocator")
    setattr(tag, "pub", "this should be in influx point dict")
    point_dict = tag.as_influx_point_dict()

    assert "measurement" in point_dict
    assert "tags" in point_dict
    assert "fields" in point_dict
    assert point_dict["fields"]["pub"] == "this should be in influx point dict"


def test_from_any_dict():
    test_vals = {
        "cpuLoad": 5.0,
        "issues": list,
        "memoryAllocated": 6.0,
        "memoryFree": 7.0,
        "memoryMax": 8.0,
        "memoryUsed": 9.1,
        "packetsPerSecond": 10.2,
        "projectName": "projname",
        "running": True,
        "udpRx": 11.2,
        "udpTx": 15.6,
        "notinc": "not me",
    }

    tag = sensor.QpeInfoData.from_any_dict(test_vals)

    assert "notinc" not in tag.__dict__
