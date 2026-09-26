#
# Title: postgres.py
# Description: postgresql support
# Development Environment: Ubuntu 22.04.5 LTS/python 3.10.12
# Author: G.S. Cole (guycole at gmail dot com)
#

import datetime
import logging
import time

from typing import List, Dict

import sqlalchemy
from sqlalchemy import and_
from sqlalchemy import func
from sqlalchemy import select
from sqlalchemy import desc

from helper.sql_table import (
    DailyScore,
    GeoLoc,
    LoadLog,
)

class PostGres:
    db_engine = None
    Session = None

    def __init__(self, logger: logging.Logger, session: sqlalchemy.orm.session.sessionmaker):
        self.logger = logger
        self.Session = session

    def daily_score_insert_or_update(self, args: dict[str, any]) -> DailyScore:
        candidate = DailyScore(args)

        try:
            with self.Session() as session:
                existing = session.scalars(
                    select(DailyScore).filter(
                        and_(
                            DailyScore.crate_name == candidate.crate_name,
                            DailyScore.host_name == candidate.host_name,
                            DailyScore.score_date == candidate.score_date,
                        )
                    )
                ).first()

                if existing is None:
                    session.add(candidate)
                else:
                    existing.file_quantity += candidate.file_quantity
                    existing.obs_quantity += candidate.obs_quantity

                session.commit()
        except Exception as error:
            self.logger.exception("daily_score_insert_or_update failed: %s", error)

        return candidate

    def geo_loc_select_by_site(self, site_name: str) -> List[GeoLoc]:
        statement = (
            select(GeoLoc)
            .filter_by(site_name=site_name)
            .order_by(desc(GeoLoc.fix_time), desc(GeoLoc.id))
        )

        with self.Session() as session:
            return session.scalars(statement).all()

    @staticmethod
    def _normalize_load_log_args(args: dict[str, any]) -> dict[str, any]:
        key_map = {
            "crateName": "crate_name",
            "epochSeconds": "epoch_seconds",
            "fileName": "file_name",
            "geoLocId": "geo_loc_id",
            "hostName": "host_name",
            "loadTime": "load_time",
            "obsQuantity": "obs_quantity",
            "obsTime": "obs_time",
            "siteName": "site_name",
            "taskName": "task",
        }

        normalized = {}
        for key, value in args.items():
            normalized[key_map.get(key, key)] = value

        return normalized

    def load_log_insert(self, args: dict[str, any]) -> LoadLog:
        normalized_args = self._normalize_load_log_args(args)
        candidate = LoadLog(normalized_args)

        try:
            with self.Session() as session:
                session.add(candidate)
                session.commit()
        except Exception as error:
            self.logger.exception("load_log_insert failed: %s", error)

        return candidate

    def load_log_select_by_file_name(self, file_name: str) -> LoadLog:
        with self.Session() as session:
            return session.scalars(
                select(LoadLog).filter_by(file_name=file_name)
            ).first()

# ;;; Local Variables: ***
# ;;; mode:python ***
# ;;; End: ***
