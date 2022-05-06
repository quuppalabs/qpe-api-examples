from dataclasses import dataclass, fields


@dataclass
class InfluxPoint:
    """This class provides the foundation for translating json
    response into a data class,  esp. from a QPE. Note: it is highly reccomended
    to implement some wrapper function for generating Influx data from
    _dict_to_influx_point_dict if the expected usage is known
    """

    @classmethod
    def from_any_dict(cls, raw_data: dict):
        """class constructor that parses out attribute value based on
        non-nested dict key names. It is reccomended for attribute names
        to break style guidelines for ease of use purposes...

        Args:
            raw_data (dict): A flat dict that 'MUST* contain at a minimum keys that match
            the dataclasses attributes with the exact same punctuation

        Returns:
            InfluxPoint: class instance of the caller
        """
        class_fields = cls.__dict__["__dataclass_fields__"].keys()
        attr_values = {
            key: val for (key, val) in raw_data.items() if key in class_fields
        }
        return cls(**attr_values)

    @staticmethod
    def dict_to_influx_point_dict(
        data: dict,
        measurement_key: str,
        tag_keys: list = None,
        fields_to_ignore: list = None,
    ) -> dict:
        """creates a dict that influx db lib can use. Every key not in measurement_key,
        nor in tag_keys will be treated as a field, nonpublic attributes, that is
        attributes that is attributes that begin with '_' are automagically ignored

        Args:
            data (dict): the dict to be formatted (dataclass.__dict__)
            measurement_key (str): the key to group by
            tag_keys (list, optional): the list of tag keys. Defaults to None.
            fields_to_ignore (list, optional): list fields not to use. Defaults to None.

        Returns:
            dict: the influx dict, i.e.:
            dict_structure = {
                    "measurement": "h2o_feet",
                    "tags": {"location": "coyote_creek"},
                    "fields": {"water_level": 1.0},
                }
        """
        if tag_keys == None:
            tag_keys = []
        if fields_to_ignore == None:
            fields_to_ignore = []

        return {
            "measurement": measurement_key,
            "tags": {key: val for (key, val) in data.items() if key in tag_keys},
            "fields": {
                key: val
                for (key, val) in data.items()
                if (
                    key not in tag_keys
                    and key != measurement_key
                    and key not in fields_to_ignore
                )
            },
        }

    def _get_non_public_attrs(self) -> list:
        return [key for key in self.__dict__.keys() if key[0] == "_"]

    def as_influx_point_dict(
        self,
        data: dict = None,
        measurement_key: str = None,
        tag_keys: list = None,
        fields_to_ignore: list = None,
    ) -> dict:
        if fields_to_ignore == None:
            fields_to_ignore = self._get_non_public_attrs()
        else:
            fields_to_ignore += self._get_non_public_attrs()

            if data == None:
                data = self.__dict__

            if measurement_key == None:
                measurement_key = self.__class__

        return self.dict_to_influx_point_dict(
            data, measurement_key, tag_keys, fields_to_ignore
        )


@dataclass
class QpeInfoData(InfluxPoint):
    cpuLoad: float
    issues: list
    memoryAllocated: float
    memoryFree: float
    memoryMax: float
    memoryUsed: float
    packetsPerSecond: float
    projectName: str
    running: bool
    udpRx: float
    udpTx: float

    def __post_init__(self):
        self.percentMemoryUsed = self.memoryUsed / self.memoryMax
        delattr(self, "memoryMax")
        self.memoryAllocated /= 1024.0
        self.memoryFree /= 1024.0
        self.memoryUsed /= 1024.0

    def as_influx_point_dict(
        self,
        data: dict = None,
        measurement_key: str = "projectName",
        tag_keys: list = None,
        fields_to_ignore: list = None,
    ) -> dict:
        if data == None:
            data = self.__dict__
        return super.as_influx_point_dict(
            data, measurement_key, tag_keys, fields_to_ignore
        )


@dataclass
class GatewayTag(InfluxPoint):
    tagId: str
    advertisingDataPayload: str
    advertisingDataPayloadTS: int
    advertisingDataPayloadSignalStrength: float
    advertisingDataPayloadLocatorId: str
    advertisingDataPayloadLocatorName: str
