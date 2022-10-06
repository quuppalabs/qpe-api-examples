""" A module for converting data from a typical QPE data point to an influx point

    This module is intended to be used as a helper for the data extracted from the QPE
    API. The data is intended to be used with the influx_db_client module to post
    data to an influx db instance.
"""

import importlib
import json
import warnings
from ast import Raise
from dataclasses import dataclass, fields
from functools import cache
from pathlib import Path
from re import VERBOSE, Match, compile, match
from types import ModuleType


@dataclass
class InfluxPoint:
    """This class provides the foundation for translating a json
    response into a data class, esp. from a QPE.
    """

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
        if tag_keys is None:
            tag_keys = []
        if fields_to_ignore is None:
            fields_to_ignore = []

        return {
            "measurement": measurement_key,
            "tags": {key: val for (key, val) in data.items() if key in tag_keys},
            "fields": {
                key: val
                for (key, val) in data.items()
                if (key not in tag_keys and key != measurement_key and key not in fields_to_ignore)
            },
        }

    @classmethod
    def from_any_dict(cls, raw_data: dict):
        """class constructor that parses out attribute value based on
        non-nested dict key names. It is reccomended for attribute names
        to break style guidelines for ease of use purposes...

        Args:
            raw_data (dict): A flat dict that 'MUST* contain at a minimum keys that match
                the dataclasses attributes with the exact same punctuation except a leading
                underscore is ignored on class attributes, and therefor should not be in
                any input data dict keys...

        Returns:
            InfluxPoint (InfluxPoint): class instance of the caller
        """
        # get the field names
        class_fields = list(cls.__dict__["__dataclass_fields__"].keys())

        # drop the leading '_'
        class_fields = list(map(lambda x: x[1::] if x[0] == "_" else x, class_fields))

        attr_values = {key: val for (key, val) in raw_data.items() if key in class_fields}

        return cls(**attr_values)

    def _get_non_public_attrs(self) -> list:
        """nonpublic function returning all attributes beggining with '_'

        Returns:
            list: list of nonpublic attributes
        """
        return [key for key in self.__dict__.keys() if key[0] == "_"]

    def as_influx_point_dict(
        self,
        instance_attrs: dict = None,
        measurement_key: str = None,
        tag_keys: list = None,
        fields_to_ignore: list = None,
    ) -> dict:
        """This function is a basic coverall of pushing attributes of the data class
        into a influx_db data point with sane defaults. All public attrubutes
        will become fields if not specified as the measurement key nor tags
        otherwise the class name is the measurement key and there are no default tags

        Args:
            instance_attrs (dict, optional): Functions as an override to specify keys
                for fields in the returned dict. Defaults to all public attributes.
            measurement_key (str, optional): Defaults to Class Name.
            tag_keys (list, optional): keys to look up as tags. Defaults to None.
            fields_to_ignore (list, optional): Keys that will not be aggregated.
                Defaults to nonpublic attribute names.

        Returns:
            dict: in the format of an influx_db point
        """
        if fields_to_ignore is None:
            fields_to_ignore = self._get_non_public_attrs()
        else:
            fields_to_ignore += self._get_non_public_attrs()

        if instance_attrs is None:
            instance_attrs = self.__dict__

        if measurement_key is None:
            measurement_key = "GatewayTags"

        return self.dict_to_influx_point_dict(instance_attrs, measurement_key, tag_keys, fields_to_ignore)


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
        """overrides base class method and left overly generalized for
        ease of later extension

        Args:
            data (dict, optional): Functions as an override to specify keys
            measurement_key (str, optional): Defaults to Class Name.
            tag_keys (list, optional): keys to look up as tags. Defaults to None.
            fields_to_ignore (list, optional): Keys that will not be aggregated.
                Defaults to nonpublic attribute names.

        Returns:
            dict: in the format of an influx_db point
        """
        if data is None:
            data = self.__dict__
        return super().as_influx_point_dict(data, measurement_key, tag_keys, fields_to_ignore)


@dataclass
class GatewayTag(InfluxPoint):
    """Class that handles converting a json dict into
    class field values and finding a parser for
    the data given. Finding the correct parser is done after
    creation, but could be done before hand to aid in extension
    via inheritance. The module function: get_parser_for_tag_id
    is external and cached for this purpose...
    """

    tagId: str
    advertisingDataPayload: str
    advertisingDataPayloadTS: int
    advertisingDataPayloadSignalStrength: float
    advertisingDataPayloadLocatorId: str
    advertisingDataPayloadLocatorName: str
    _packet_type: str = None

    def tokenize_data(self, device_type: str = None, parser: ModuleType = None) -> bool:
        """attempts to load a parser if none is provided and then
        tokenize the data accordingly. If the parsing could not complete
        False is returned otherwise true

        Args:
            parser (dict, optional): The parser dict to use. Defaults to None.

        Returns:
            bool: False on failure to parse, True on success
        """

        adv_data = "".join([byte[2::] for byte in self.advertisingDataPayload.split(" ")])  # 0xbe 0xac ... -> beac...

        if not parser:
            parser = self.get_parser_for_tag_id(self.tagId, adv_data, device_type)

        if not parser:  # if a parser could not me identified
            return False

        if result := match(parser.tokens_reg_ex, adv_data, VERBOSE):
            setattr(self, "_parser", parser)  # store token to instance attributes
            self._packet_type = parser.__name__.split(".")[2]

            # every post proc module must implement this function
            values: dict = parser.process_adv_data(result)

            for (name, val) in values.items():
                setattr(self, name, val)  # store values as attributes pm this class instance

            return True

        else:  # adv data did not match the format expected by parser
            return False

    @staticmethod
    def get_parser_for_tag_id(id: str, payload: str, device_type: str = None) -> ModuleType:
        """parses files in parsers/ dir until tag id
        that is associated with a parser is found. Alternatively
        if and ID based match isn't made an attempt to match based
        on the packet format is also made.

        Args:
            id (str): tag id to be found

        Returns:
            dict: parser if found, empty dict otherwise
        """

        for fp in Path("src/sensortags/parsers").iterdir():
            if device_type == fp.stem:
                try:
                    parser_mod = importlib.import_module(f"sensortags.parsers.{fp.stem}")

                    return parser_mod

                except ImportError:
                    warnings.warn(
                        f"""A device type was specified for device id: {id} 
                        but a parser could not be found. 
                        Maybe the type name was misspelled...""",
                    )
                    return None

            elif fp.suffix == ".py":
                try:
                    if "init" not in fp.stem:
                        parser_mod = importlib.import_module(f"sensortags.parsers.{fp.stem}")

                    else:
                        continue

                    if match(parser_mod.tokens_reg_ex, payload, VERBOSE):
                        return parser_mod

                except ImportError as e:
                    # if a post proc module could not be found this is
                    # almost 100% a critical error
                    raise ImportError(f"{fp.name} should be an importable module but is not") from e

        return None

    def as_influx_point_dict(
        self,
        fields: dict = None,
        measurement_key: str = None,
        tag_keys: list = None,
        fields_to_ignore: list = None,
    ) -> dict:
        """formatting override to base class method"""
        if not fields_to_ignore:
            fields_to_ignore = [
                "advertisingDataPayload",
                "advertisingDataPayloadTS",
                "advertisingDataPayloadSignalStrength",
                "advertisingDataPayloadLocatorName",
            ]
        else:
            fields_to_ignore += [
                "advertisingDataPayload",
                "advertisingDataPayloadTS",
                "advertisingDataPayloadSignalStrength",
                "advertisingDataPayloadLocatorName",
            ]

        return super().as_influx_point_dict(
            fields,
            self._packet_type,
            tag_keys,
            fields_to_ignore,
        )
