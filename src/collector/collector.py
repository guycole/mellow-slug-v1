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

from typing import Any

import yaml
from yaml.loader import SafeLoader

from abc import ABC, abstractmethod

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("slug")


class Equipment(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(populate_by_name=True)

    host_name: str = pydantic.Field(alias="hostName")
    host_type: str = pydantic.Field(alias="hostType")


class GeoLoc(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(populate_by_name=True)

    altitude: float
    latitude: float
    longitude: float
    site_name: str = pydantic.Field(alias="siteName")


class Job(pydantic.BaseModel):
    mode: str
    project: str
    task: str


class Observation(pydantic.BaseModel):
    name: str


class Receiver(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(populate_by_name=True)

    antenna: str
    receiver_id: int = pydantic.Field(alias="receiverId")
    task: str
    type: str


class TimeStamp(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(populate_by_name=True)

    epoch_seconds: int = pydantic.Field(default_factory=lambda: int(time.time()), alias="epochSeconds")
    iso8601: str = ""

    @pydantic.model_validator(mode="after")
    def sync_iso8601_from_epoch(self) -> "TimeStamp":
        self.iso8601 = datetime.datetime.fromtimestamp(
            self.epoch_seconds, tz=zoneinfo.ZoneInfo("UTC")
        ).isoformat()
        return self


class SlugModel(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(populate_by_name=True)

    crate_name: str = pydantic.Field(alias="crateName")
    file_name: str = pydantic.Field(alias="fileName")
    version: int = 1
    equipment: Equipment
    geo_loc: GeoLoc = pydantic.Field(alias="geoLoc")
    job: Job
    receiver: Receiver
    time_stamp: TimeStamp = pydantic.Field(alias="timeStamp")
    observations: list[Observation]


class Collector(ABC):
    @abstractmethod
    def get_observations(self) -> list[Observation]:
        pass

    @abstractmethod
    def execute(self) -> int:
        pass


class SlugCollector(Collector):
    def __init__(self, args: dict[str, Any]):
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
        logger.info("collector execute: %s", self.receiver.task)

        base_file_name = str(uuid.uuid4())
        logger.info("base filename: %s", base_file_name)

        outfile_json = f"{self.fresh_dir}/{base_file_name}.json"

        slug_model = SlugModel(
            crate_name=self.crate_name,
            file_name=f"{base_file_name}.json",
            equipment=self.equipment,
            geo_loc=self.geo_loc,
            job=self.job,
            receiver=self.receiver,
            time_stamp=self.time_stamp,
            observations=self.get_observations(),
        )

        with open(outfile_json, "w", encoding="utf-8") as out_file:
            out_file.write(slug_model.model_dump_json(indent=4, by_alias=True))

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
            logger.error("YAML parse error: %s", error)

    exit(1)

# ;;; Local Variables: ***
# ;;; mode:python ***
# ;;; End: ***
