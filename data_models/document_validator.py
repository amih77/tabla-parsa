from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any

from pydantic import BaseModel, model_validator, Field

from odm_models.disrcrepancy import Discrepancy
from odm_models.document import Document
from utils.common import get_config, ValidationStatus, ValidationName


class ValidationStrategy(ABC, BaseModel):
    cfg: dict = Field(default_factory=get_config)

    @abstractmethod
    def validate(self, document: Document) -> tuple[bool, str | None, str | None]:
        pass


class HeaderValidator(ValidationStrategy):
    def validate(self, document: Document) -> tuple[bool, str | None, str | None]:
        min_length = self.cfg["discrepancies"]["validation_params"]["header"][
            "min_length"
        ]
        return (
            (False, "header", f"len({document.title} < {min_length})")
            if len(document.title) < min_length
            else (True, None, None)
        )


class FooterValidator(ValidationStrategy):
    def validate(self, document: Document) -> tuple[bool, str | None, str | None]:
        max_date = datetime.fromisoformat(
            self.cfg["discrepancies"]["validation_params"]["footer"]["max_date"]
        )
        return (
            (
                False,
                "footer",
                f"{document.date_of_creation.isoformat()} is after {max_date.isoformat()})",
            )
            if document.date_of_creation > max_date
            else (True, None, None)
        )


class RowsValidator(ValidationStrategy):
    def validate(self, document: Document) -> tuple[bool, str | None, str | None]:
        max_sum = self.cfg["discrepancies"]["validation_params"]["rows"][
            "max_first_row_sum"
        ]

        return (
            (
                False,
                "first_row" f"{document.rows[0]} sum is greater than {max_sum})",
            )
            if sum([val[0] for val in document.rows[0]]) > max_sum
            else (True, None, None)
        )


validator_name_to_class = {
    ValidationName.HEADER: HeaderValidator,
    ValidationName.FOOTER: FooterValidator,
    ValidationName.ROWS: RowsValidator,
}


class DocumentValidator(BaseModel):
    document_id: str
    document: Document = None
    status: ValidationStatus = ValidationStatus.NOT_PROCESSED
    validations: list[ValidationName] = None

    @model_validator(mode="after")
    def update_fields(self) -> Any:
        cfg = get_config()
        self.validations = [
            ValidationName(validator_name)
            for validator_name in cfg["discrepancies"]["validations_to_compute"]
        ]
        self.document = Document.from_db(self.document_id)
        return self

    def validate_(self) -> tuple[ValidationStatus, dict | None]:
        if not self.document:
            return ValidationStatus.NOT_FOUND, None
        if self.document.validation_status is not ValidationStatus.NOT_PROCESSED:
            raise Exception(f"Cant validate a validated document. status: {self.document.validation_status}")
        results = {}
        for validation_name in self.validations:
            try:
                result, location, msg = validator_name_to_class[
                    validation_name
                ]().validate(self.document)
                if not result:
                    results[validation_name.value] = msg
                    self.status = ValidationStatus.INVALID
                    self.create_discrepancy(validation_name, location, msg)
            except Exception as e:
                self.status = ValidationStatus.ERROR
                self.create_discrepancy(
                    validation_name,
                    validation_name.value,
                    f"{validation_name.value} erred. {e}",
                )

        return self.status if results else ValidationStatus.VALID, results

    def create_discrepancy(
        self, validation_name: ValidationName, location: str, msg: str
    ):
        discrepancy = Discrepancy(
            document_id=self.document_id,
            discrepancy_type=validation_name,
            location=location,
            details=msg,
        )
        discrepancy.to_db()

    @staticmethod
    def validate_and_update(document_id: str):
        try:
            validator = DocumentValidator(document_id=document_id)
            status, _ = validator.validate_()
            Document.update(document_id, {"validation_status": status.name})
        except Exception as e:
            print(f"Could not validate document {document_id}. {e}")
