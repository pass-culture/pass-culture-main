from typing import List

from pcapi.core.offers.models import ComplianceValidationStatusPrediction
from pcapi.routes.serialization import BaseModel


class GetComplianceScoreRequest(BaseModel):
    offer_id: str
    offer_name: str | None = None
    offer_description: str | None = None
    offer_subcategory_id: str | None = None
    rayon: str | None = None
    macro_rayon: str | None = None
    stock_price: float | None = None
    image_url: str | None = None
    offer_type_label: str | None = None
    offer_sub_type_label: str | None = None
    author: str | None = None
    performer: str | None = None

    def to_dict(self) -> dict:
        return {
            "offer_id": self.offer_id,
            "offer_name": self.offer_name,
            "offer_description": self.offer_description,
            "offer_subcategory_id": self.offer_subcategory_id,
            "rayon": self.rayon,
            "macro_rayon": self.macro_rayon,
            "stock_price": self.stock_price,
            "image_url": self.image_url,
            "offer_type_label": self.offer_type_label,
            "offer_sub_type_label": self.offer_sub_type_label,
            "author": self.author,
            "performer": self.performer,
        }


class ComplianceScorePredictionOutput(BaseModel):
    probability_validated: int | None
    validation_main_features: List[str] | None
    probability_rejected: int | None
    rejection_main_features: List[str] | None


class ComplianceValidationStatusPredictionOutput(BaseModel):
    validation_status_prediction: ComplianceValidationStatusPrediction | None
    validation_status_prediction_reason: str | None


class CompliancePredictionOutput(ComplianceScorePredictionOutput, ComplianceValidationStatusPredictionOutput):
    pass


class SearchOffersRequest(BaseModel):
    query: str
    filters: list[dict]


class SearchOfferResponse(BaseModel):
    offer_id: int
    pertinence: str


class SearchOffersResponse(BaseModel):
    results: list[SearchOfferResponse]
