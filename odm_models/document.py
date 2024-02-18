import re
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from odm_models.disrcrepancy import Discrepancy
from odm_models.odm_interface import OdmInterface
from utils.common import DocumentType, ValidationStatus

from utils.mongodb_utils import MongoDBUtils


class DocumentUpdate(BaseModel):
    validation_status: ValidationStatus | None = None
    is_archived: bool | None = None
    title: str | None = None
    row_headers: list[str] | None = None
    col_headers: list[str] | None = None
    footer: str | None = None
    values: list[list[tuple[float, str | None]]] | None = None

    model_config = ConfigDict(
        use_enum_values=True, populate_by_name=True, validate_default=True
    )


class Document(OdmInterface):
    @classmethod
    def collection_name(cls):
        return "documents"

    validation_status: ValidationStatus = ValidationStatus.NOT_PROCESSED
    type: DocumentType
    title: str | None
    row_headers: list[str] | None
    col_headers: list[str] | None
    footer: str | None
    values: list[list[tuple[float, str | None]]] | None
    path: str

    @property
    def country_of_creation(self) -> str | None:
        pattern = r"Creation:.* (\w+)$"
        try:
            footer_match = re.search(pattern, self.footer)
            return footer_match.group(1)
        except Exception:
            return None

    @property
    def date_of_creation(self) -> datetime | None:
        pattern = r"Creation: (\d{1,2}[a-zA-Z]{3}\d{4})"
        try:
            footer_match = re.search(pattern, self.footer)
            return datetime.strptime(footer_match.group(1), "%d%b%Y")
        except Exception:
            return None

    @staticmethod
    def update(id_: str, update_data: dict):
        update_dict = DocumentUpdate(**update_data).model_dump(exclude_none=True)
        MongoDBUtils().update(Document.collection_name(), {"id_": id_}, update_dict)

    @property
    def discrepancies(self) -> list[Discrepancy]:
        data: list[dict] = MongoDBUtils().fetch(
            collection_name=Discrepancy.collection_name(),
            filter_={"document_id": self.id_},
            single_result=False,
        )
        return [Discrepancy(**discrepancy_data) for discrepancy_data in data]
