from dataclasses import dataclass, fields


@dataclass
class QpeData:
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

    @classmethod
    def from_any_dict(cls, raw_data: dict):
        class_annotations = cls.__dict__["__annotations__"].keys()
        attr_values = {
            key: val for (key, val) in raw_data.items() if key in class_annotations
        }
        return cls(**attr_values)

    @staticmethod
    def dict_to_influx_point_dict(
        data: dict, measurement_key: str, tag_keys: list = []
    ) -> dict:
        return {
            "measurement": data[measurement_key],
            "tags": {key: val for (key, val) in data.items() if key in tag_keys},
            "fields": {
                key: val
                for (key, val) in data.items()
                if (key not in tag_keys and key != measurement_key)
            },
        }

    def __post_init__(self):
        self.percentMemoryUsed = self.memoryUsed / self.memoryMax
        delattr(self, "memoryMax")
        self.memoryAllocated /= 1024.0
        self.memoryFree /= 1024.0
        self.memoryUsed /= 1024.0

    def as_influx_point_dict(self) -> dict:
        return self.dict_to_influx_point_dict(self.__dict__, "projectName")
