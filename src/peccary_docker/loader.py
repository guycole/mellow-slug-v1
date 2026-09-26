#
# Title: loader.py
# Description: load heeler files
# Development Environment: Ubuntu 22.04.5 LTS/python 3.10.12
# Author: G.S. Cole (guycole at gmail dot com)
#
import logging
import datetime
import json
import os

from abc import ABC, abstractmethod

from helper.json_helper import JsonHelper
from helper.postgres import PostGres

class Loader(ABC):
    @abstractmethod
    def file_processor(self, file_name: str) -> bool:
        pass

    @abstractmethod
    def execute(self) -> int:
        pass

    @abstractmethod
    def file_failure(self, file_name: str) -> None:
        pass

    @abstractmethod
    def file_success(self, file_name: str) -> None:
        pass

    @abstractmethod
    def load_log_test(self, test_file_name: str) -> bool:
        pass

class SlugLoader(Loader):

    def __init__(self, logger: logging.Logger, postgres: PostGres):
        self.logger = logger
        self.postgres = postgres

        self.failure_dir = os.environ.get("FAILURE_DIR", "/var/peccary/hyena/failure")
        self.fresh_dir = os.environ.get("FRESH_DIR", "/var/peccary/hyena/hyena-v2")

        self.failure = 0
        self.success = 0

        self.jh = JsonHelper(logger)

    def file_failure(self, file_name: str):
        #        logger.info(f"file failure:{file_name}")

        self.failure += 1
        os.rename(file_name, self.failure_dir + "/" + file_name)

    def file_success(self, file_name: str):
        #        logger.info(f"file success:{file_name}")

        self.success += 1
        os.remove(file_name)

    def load_log_test(self, test_file_name: str) -> bool:
        self.logger.info(f"load_log_test for file: {test_file_name}")

        try:
            candidate = self.postgres.load_log_select_by_file_name(test_file_name)
            if candidate is None:
                self.logger.info(f"processing new file:{test_file_name}")

                geo_loc = self.postgres.geo_loc_select_by_site(self.jh.raw_json["geoLoc"]["siteName"])
                if len(geo_loc) == 0:
                    self.logger.warning("must insert geo_loc for site: %s", self.jh.raw_json["geoLoc"]["siteName"],)
                    return False

                load_log = {
                    "crate_name": self.jh.raw_json["crateName"],
                    "epoch_seconds": self.jh.raw_json["timeStamp"]["epochSeconds"],
                    "file_name": test_file_name,
                    "geo_loc_id": geo_loc[0].id,
                    "host_name": self.jh.raw_json["equipment"]["hostName"],
                    "load_time": datetime.datetime.now(),
                    "mode": self.jh.raw_json["job"]["mode"],
                    "obs_quantity": len(self.jh.raw_json["observations"]),
                    "obs_time": self.jh.raw_json["timeStamp"]["iso8601"],
                    "site_name": self.jh.raw_json["geoLoc"]["siteName"],
                    "task": self.jh.raw_json["job"]["task"],
                }

                self.postgres.load_log_insert(load_log)

                daily_score = {
                    "crate_name": self.jh.raw_json["crateName"],
                    "file_quantity": 1,
                    "host_name": self.jh.raw_json["equipment"]["hostName"],
                    "obs_quantity": len(self.jh.raw_json["observations"]),
                    "score_date": datetime.datetime.fromisoformat(self.jh.raw_json["timeStamp"]["iso8601"]).date(),
                }

                self.postgres.daily_score_insert_or_update(daily_score)

                return True
            else:
                self.logger.info(f"skippping already processed:{test_file_name}")
        except Exception as error:
            self.logger.error(f"postgres insert failed for {test_file_name}: {error}")
        
        return False

    def file_processor(self, file_name) -> bool:
        self.logger.info(f"processing file:{file_name}")

        if not self.jh.json_file_tester(file_name):
            self.file_failure(file_name)
            return False

        if self.load_log_test(file_name):
            self.file_success(file_name)
            return True
        else:
            self.file_failure(file_name)
            return False

    def execute(self) -> int:
        self.logger.info(f"loader fresh dir:{self.fresh_dir}")

        os.chdir(self.fresh_dir)
        targets = sorted(os.listdir("."))
        self.logger.info(f"{len(targets)} files noted")

        for target in targets:
            self.file_processor(target)

        self.logger.info(f"loader success:{self.success} failure:{self.failure}")

        return 0

# ;;; Local Variables: ***
# ;;; mode:python ***
# ;;; End: ***
