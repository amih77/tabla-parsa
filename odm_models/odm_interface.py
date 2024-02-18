from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional
from uuid import uuid4

from pydantic import BaseModel, Field

from utils.mongodb_utils import MongoDBUtils


# object document mapper interface
class OdmInterface(BaseModel, ABC):
    id_: str = Field(default_factory=lambda: str(uuid4()), alias="_id")
    ts: datetime = Field(default_factory=datetime.now)
    is_archived: bool = False

    class Config:
        populate_by_name = True

    @classmethod
    @abstractmethod
    def collection_name(cls):
        pass

    def to_dict(self) -> dict:
        return self.model_dump(by_alias=True)

    def to_db(self):
        id_ = MongoDBUtils().insert(self.__class__.collection_name(), self.model_dump(by_alias=True))
        assert id_ == self.id_

    @classmethod
    def from_db(cls, id_: str) -> Optional["OdmInterface"]:
        obj = MongoDBUtils().fetch(
            collection_name=cls.collection_name(),
            filter_={"_id": id_},
            single_result=True
        )
        return obj and cls(**obj)
