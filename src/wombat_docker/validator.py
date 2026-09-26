#
# Title: validator.py
# Description: ensure valid slug files
# Development Environment: Ubuntu 22.04.5 LTS/python 3.10.12
# Author: G.S. Cole (guycole at gmail dot com)
#
import logging
import datetime
import os

from abc import ABC, abstractmethod

from helper.json_helper import JsonHelper
from helper.postgres import PostGres


class Validator(ABC):

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


class SlugValidator(Validator):

    def __init__(self, logger: logging.Logger, postgres: PostGres):
        self.logger = logger
        self.postgres = postgres
        self.json_helper = JsonHelper(logger)

        self.failure_dir = os.environ.get("FAILURE_DIR", "/var/wombat/failure")
        self.fresh_dir = os.environ.get("FRESH_DIR", "/var/wombat/fresh/slug")
        self.success_dir = os.environ.get("SUCCESS_DIR", "/var/wombat/slug/success")

        self.failure = 0
        self.success = 0

    def file_failure(self, file_name: str) -> None:
        self.logger.info(f"file failure:{file_name}")

        self.failure += 1
        failure_target = os.path.join(self.failure_dir, file_name)
        try:
            os.rename(file_name, failure_target)
        except Exception as error:
            self.logger.error(f"file move failure for {file_name} -> {failure_target}: {error}")

    def file_success(self, file_name: str) -> None:
        self.logger.info(f"file success:{file_name}")

        self.success += 1
        success_target = os.path.join(self.success_dir, file_name)
        try:
            os.rename(file_name, success_target)
        except Exception as error:
            self.logger.error(f"file move failure for {file_name} -> {success_target}: {error}")

    def load_log_test(self, test_file_name: str) -> bool:
        try:
            raw_buffer = self.json_helper.raw_json

            self.logger.info(f"checking load log:{test_file_name}")

            candidate = self.postgres.load_log_select_by_file_name(test_file_name)
            if candidate is not None:
                self.logger.info(f"skipping already processed:{test_file_name}")
                return False
            else:
                crate_name = raw_buffer["crateName"]
                host_name = raw_buffer["equipment"]["hostName"]
                site_name = raw_buffer["geoLoc"]["siteName"]
                task_name = raw_buffer["receiver"]["task"]
                obs_quantity = len(raw_buffer["observations"])
                obs_time = raw_buffer["timeStamp"]["iso8601"]

                geo_loc_matches = self.postgres.geo_loc_select_by_site(site_name)
                if len(geo_loc_matches) < 1:
                    self.logger.error(f"missing geo location for site:{site_name}")
                    return False

                geo_loc_id = geo_loc_matches[0].id

                load_log = {
                    "crate_name": crate_name,
                    "epoch_seconds": raw_buffer["timeStamp"]["epochSeconds"],
                    "file_name": test_file_name,
                    "geo_loc_id": geo_loc_id,
                    "host_name": host_name,
                    "load_time": datetime.datetime.now(),
                    "obs_quantity": obs_quantity,
                    "obs_time": obs_time,
                    "site_name": site_name,
                    "task": task_name,
                }

                self.postgres.load_log_insert(load_log)

                daily_score = {
                    "crate_name": crate_name,
                    "file_quantity": 1,
                    "host_name": host_name,
                    "obs_quantity": obs_quantity,
                    "score_date": datetime.datetime.fromisoformat(obs_time).date(),
                }
                self.postgres.daily_score_insert_or_update(daily_score)

                self.logger.info(f"load log insert complete:{test_file_name}")

                return True
        except Exception as error:
            self.logger.error(f"postgres insert failed for {test_file_name}: {error}")
        
        return False

    def file_processor(self, file_name: str) -> bool:
        self.logger.info(f"processing file:{file_name}")

        if not self.json_helper.json_file_tester(file_name):
            self.file_failure(file_name)
            return False

        if self.load_log_test(file_name):
            self.file_success(file_name)
            return True
        else:
            self.file_failure(file_name)
            return False

    def execute(self) -> int:
        self.logger.info(f"validator fresh dir:{self.fresh_dir}")

        os.chdir(self.fresh_dir)
        targets = sorted(os.listdir("."))
        self.logger.info(f"{len(targets)} files noted")

        for target in targets:
            self.file_processor(target)

        self.logger.info(f"validator success:{self.success} failure:{self.failure}")

        return 0

# ;;; Local Variables: ***
# ;;; mode:python ***
# ;;; End: ***
