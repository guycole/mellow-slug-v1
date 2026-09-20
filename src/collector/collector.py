#
# Title: collector.py
# Description:
# Development Environment: Ubuntu 22.04.5 LTS/python 3.10.12
# Author: G.S. Cole (guycole at gmail dot com)
#

import datetime
import json
import pydantic
import logging
import sys
import time
import uuid
import zoneinfo

import yaml
from yaml.loader import SafeLoader

from abc import ABC, abstractmethod

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("slug")


class Equipment(pydantic.BaseModel):
    hostName: str
    hostType: str


class GeoLoc(pydantic.BaseModel):
    altitude: float
    latitude: float
    longitude: float
    siteName: str


class Job(pydantic.BaseModel):
    mode: str
    project: str
    task: str


class Observation(pydantic.BaseModel):
    name: str


class Receiver(pydantic.BaseModel):
    antenna: str
    receiverId: int
    task: str
    type: str


class TimeStamp(pydantic.BaseModel):
    epochSeconds: int = pydantic.Field(default_factory=lambda: int(time.time()))
    iso8601: str = ""

    @pydantic.model_validator(mode="after")
    def sync_iso8601_from_epoch(self) -> "TimeStamp":
        self.iso8601 = datetime.datetime.fromtimestamp(
            self.epochSeconds, tz=zoneinfo.ZoneInfo("UTC")
        ).isoformat()
        return self


class SlugModel(pydantic.BaseModel):
    crateName: str
    fileName: str
    version: int = 1
    equipment: Equipment
    geoLoc: GeoLoc
    job: Job
    receiver: Receiver
    timeStamp: TimeStamp
    observations: list[Observation]


class Collector(ABC):
    @abstractmethod
    def get_observations(self) -> list[Observation]:
        pass

    @abstractmethod
    def execute(self) -> int:
        pass


class SlugCollector(Collector):
    def __init__(self, args: dict[str, any]):
        self.crate_name = args["crateName"]
        self.fresh_dir = args["freshDir"]

        self.equipment = Equipment(**args["equipment"])
        self.geo_loc = GeoLoc(**args["geoLoc"])
        self.receiver = Receiver(**args["receiver"])
        self.time_stamp = TimeStamp()

        task = args["receiver"]["task"]
        mode = "default"
        project = task
        self.job = Job(mode=mode, project=project, task=task)

    def get_observations(self) -> list[Observation]:
        return []

    def execute(self) -> int:
        print(f"collector execute: {self.receiver.task}")

        base_file_name = str(uuid.uuid4())
        print(f"base filename: {base_file_name}")

        outfile_json = f"{self.fresh_dir}/{base_file_name}.json"

        observations = self.get_observations()

        slug_model = SlugModel(
            crateName=self.crate_name,
            fileName=f"{base_file_name}.json",
            equipment=self.equipment,
            geoLoc=self.geo_loc,
            job=self.job,
            receiver=self.receiver,
            timeStamp=self.time_stamp,
            observations=observations,
        )

        with open(outfile_json, "w", encoding="utf-8") as out_file:
            out_file.write(slug_model.model_dump_json(indent=4))

        return 0


#
# argv[1] = configuration filename
#
if __name__ == "__main__":
    if len(sys.argv) > 1:
        file_name = sys.argv[1]
    else:
        file_name = "config.yaml"

    with open(file_name, "r") as in_file:
        try:
            configuration = yaml.load(in_file, Loader=SafeLoader)
            collector = SlugCollector(configuration)
            exit(collector.execute())
        except yaml.YAMLError as error:
            print(error)

    exit(1)

# ;;; Local Variables: ***
# ;;; mode:python ***
# ;;; End: ***
