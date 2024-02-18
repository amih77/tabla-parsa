import os
from threading import Thread

from data_models.document_validator import DocumentValidator
from odm_models.disrcrepancy import Discrepancy
from odm_models.document import Document
from data_models.parser import HTMLParser
from utils.common import DocumentType, ValidationStatus


def create_documents(directory_path: str) -> list[str]:
    res = []
    for filename in os.listdir(directory_path):
        if os.path.isfile(os.path.join(directory_path, filename)):
            try:
                res.append(create_document(os.path.join(directory_path, filename)))
                print(f"document from {filename} created!")
            except Exception as e:
                print(f"Couldn't parse {os.path.join(directory_path, filename)}. {e}")
    return res


def validate_document_async(document_id: str):
    th = Thread(target=DocumentValidator.validate_and_update, args=(document_id, ))
    th.start()


def create_document(file_path: str) -> str:
    document, document_id = None, None
    _, file_extension = os.path.splitext(file_path)
    try:
        document_type = DocumentType(file_extension.lower())
        match document_type:
            case DocumentType.HTML:
                document = HTMLParser(file_path).parse()
            # can add here more parsers for different document types
        document.to_db()
        validate_document_async(document.id_)
        return document.id_
    except Exception as e:
        raise Exception(f"Could not create document from path {file_path}. {e}")


def delete_document(document_id: str):
    Document.update(document_id, {"is_archived": True})
    Discrepancy.update(
        Document.collection_name(), {"document_id": document_id}, {"is_archived": True}
    )


def update_document(document_id: str, data: dict):
    data["validation_status"] = ValidationStatus.NOT_PROCESSED
    Document.update(document_id, data)
    Discrepancy.update(
        Document.collection_name(), {"document_id": document_id}, {"is_archived": True}
    )
    validate_document_async(document_id)


def get_document(document_id: str) -> Document | None:
    return Document.from_db(document_id)
