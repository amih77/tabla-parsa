import json
import os
from enum import Enum


def get_config() -> dict:
    dir_path = os.path.dirname(os.path.realpath(__file__))
    config_path = os.path.join(dir_path, "config.json")
    with open(config_path) as f:
        return json.load(f)


class DocumentType(Enum):
    HTML = ".html"


class ValidationStatus(Enum):
    VALID = "valid"
    INVALID = "invalid"
    ERROR = "error"
    NOT_FOUND = "not_found"
    NOT_PROCESSED = "not_processed"


class ValidationName(Enum):
    HEADER = "header"
    ROWS = "rows"
    FOOTER = "footer"
