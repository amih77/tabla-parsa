from odm_models.odm_interface import OdmInterface
from utils.common import ValidationName


class Discrepancy(OdmInterface):
    document_id: str
    discrepancy_type: ValidationName
    details: str
    location: str

    @classmethod
    def collection_name(cls) -> str:
        return "discrepancies"
