from typing import List

from pydantic import BaseModel as BaseModelV2

from pcapi.core.offers.models import ComplianceValidationStatusPrediction


class UpdateOfferComplianceScorePayload(BaseModelV2):
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


class ComplianceScorePredictionOutput(BaseModelV2):
    probability_validated: int | None = None
    validation_main_features: List[str] | None = None
    probability_rejected: int | None = None
    rejection_main_features: List[str] | None = None


class ComplianceValidationStatusPredictionOutput(BaseModelV2):
    validation_status_prediction: ComplianceValidationStatusPrediction | None = None
    validation_status_prediction_reason: str | None = None


class CompliancePredictionOutput(ComplianceScorePredictionOutput, ComplianceValidationStatusPredictionOutput):
    pass


class SearchOffersRequest(BaseModelV2):
    query: str
    filters: list[dict]


class SearchOfferResponse(BaseModelV2):
    offer_id: int
    pertinence: str


class SearchOffersResponse(BaseModelV2):
    results: list[SearchOfferResponse]
