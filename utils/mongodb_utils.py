import os
import time
from enum import Enum
from typing import Union

import certifi as certifi

from dataclasses import dataclass, field
from pymongo import MongoClient
from urllib.parse import quote_plus
from pymongo.collection import Collection

from utils import common


def sanitize_data(data: dict):
    for k, v in data.items():
        if isinstance(v, Enum):
            data[k] = v.value


@dataclass
class MongoDBUtils:
    cfg: dict = field(default_factory=common.get_config)

    def get_client(self) -> MongoClient:
        uri = self.cfg["db"]["uri"].format(
            username=quote_plus(os.getenv("MONGODB_USERNAME")),
            password=quote_plus(os.getenv("MONGODB_PASSWORD")),
        )
        return MongoClient(uri, tlsCAFile=certifi.where())

    def get_collection(self, collection_name: str) -> Collection:
        db = self.get_client()[self.cfg["db"]["name"]]
        return db[collection_name]

    def insert(self, collection_name: str, data: dict) -> str:
        sanitize_data(data)
        result = self.get_collection(collection_name).insert_one(data)
        return result.inserted_id

    def fetch(
        self, collection_name: str, filter_: dict, single_result: bool
    ) -> Union[list[dict | None], dict | None]:
        sanitize_data(filter_)
        filter_["is_archived"] = False
        data = self.get_collection(collection_name).find(filter=filter_)
        return data[0] if single_result else data

    def update(self, collection_name: str, filter_: dict, update_data: dict):
        sanitize_data(filter_)
        sanitize_data(update_data)
        collection = self.get_collection(collection_name)
        filter_["is_archived"] = True
        result = collection.update_many(filter_, {"$set": update_data})

        if not result.matched_count:
            raise Exception("could not update")
