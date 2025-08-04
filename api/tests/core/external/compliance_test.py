import logging
from unittest import mock

import pytest
import sqlalchemy.orm as sa_orm

from pcapi.core.categories import subcategories
from pcapi.core.external import compliance
from pcapi.core.external.compliance_backends.compliance import ComplianceBackend
from pcapi.core.offers import factories as offers_factories
from pcapi.core.offers import models as offers_models
from pcapi.core.testing import assert_num_queries
from pcapi.models import db
from pcapi.utils import requests


pytestmark = pytest.mark.usefixtures("db_session")


@pytest.mark.usefixtures("db_session")
class GetDataComplianceScoringTest:
    @mock.patch("pcapi.core.external.compliance.compliance_backend", ComplianceBackend())
    @mock.patch("pcapi.core.auth.api.get_id_token_from_google", return_value="Good token")
    def test_get_data_compliance_scoring(self, mock_get_id_token_from_google, requests_mock):
        requests_mock.post(
            "https://compliance.passculture.team/latest/model/compliance/scoring",
            json={"probability_validated": 50, "rejection_main_features": ["stock_price", "offer_description"]},
        )
        offer = offers_factories.OfferFactory(name="Hello la data")
        payload = compliance._get_payload_for_compliance_api(offer)
        compliance.make_update_offer_compliance_score(payload)
        offer_compliance = db.session.query(offers_models.OfferCompliance).filter_by(offerId=offer.id).one()
        assert offer_compliance.compliance_score == 50
        assert offer_compliance.compliance_reasons == ["stock_price", "offer_description"]
        assert offer_compliance.validation_status_prediction is None
        assert offer_compliance.validation_status_prediction_reason is None

    @mock.patch("pcapi.core.external.compliance.compliance_backend", ComplianceBackend())
    @mock.patch("pcapi.core.auth.api.get_id_token_from_google", return_value="Good token")
    def test_upsert_compliance_scoring(self, mock_get_id_token_from_google, requests_mock):
        requests_mock.post(
            "https://compliance.passculture.team/latest/model/compliance/scoring",
            json={"probability_validated": 50, "rejection_main_features": ["offer_name"]},
        )
        offer = offers_factories.OfferFactory(
            name="Hello la data",
        )
        offers_factories.OfferComplianceFactory(
            offer=offer, compliance_score=30, compliance_reasons=["stock_price", "offer_description"]
        )
        payload = compliance._get_payload_for_compliance_api(offer)
        compliance.make_update_offer_compliance_score(payload)
        offer_compliance = db.session.query(offers_models.OfferCompliance).filter_by(offerId=offer.id).one()
        assert offer_compliance.compliance_score == 50
        assert offer_compliance.compliance_reasons == ["offer_name"]
        assert offer_compliance.validation_status_prediction is None
        assert offer_compliance.validation_status_prediction_reason is None

    @mock.patch("pcapi.core.external.compliance.compliance_backend", ComplianceBackend())
    @mock.patch("pcapi.core.auth.api.get_id_token_from_google", return_value="Good token")
    def test_get_data_compliance_scoring_without_reasons(self, mock_get_id_token_from_google, requests_mock):
        requests_mock.post(
            "https://compliance.passculture.team/latest/model/compliance/scoring",
            json={"probability_validated": 50, "rejection_main_features": []},
        )
        offer = offers_factories.OfferFactory(name="Hello la data")
        payload = compliance._get_payload_for_compliance_api(offer)
        compliance.make_update_offer_compliance_score(payload)
        offer_compliance = db.session.query(offers_models.OfferCompliance).filter_by(offerId=offer.id).one()
        assert offer_compliance.compliance_score == 50
        assert offer_compliance.compliance_reasons == []
        assert offer_compliance.validation_status_prediction is None
        assert offer_compliance.validation_status_prediction_reason is None

    @mock.patch("pcapi.core.external.compliance.compliance_backend", ComplianceBackend())
    @mock.patch("pcapi.core.auth.api.get_id_token_from_google", return_value="Good token")
    def test_get_data_compliance_scoring_with_failed_auth_exception(self, mock_requests_post, requests_mock, caplog):
        requests_mock.post("https://compliance.passculture.team/latest/model/compliance/scoring", status_code=401)
        offer = offers_factories.OfferFactory(name="Hello la data")
        payload = compliance._get_payload_for_compliance_api(offer)

        with caplog.at_level(logging.ERROR):
            with pytest.raises(requests.ExternalAPIException) as exc:
                compliance.make_update_offer_compliance_score(payload)

        assert exc.value.is_retryable is False
        assert caplog.records[0].message == "Connection to Compliance API was refused"
        assert caplog.records[0].extra == {"status_code": 401}
        assert not db.session.query(offers_models.OfferCompliance).filter_by(offerId=offer.id).count()

    @mock.patch("pcapi.core.external.compliance.compliance_backend", ComplianceBackend())
    @mock.patch("pcapi.core.auth.api.get_id_token_from_google", return_value="Good token")
    def test_get_data_compliance_scoring_with_bad_data_exception(self, mock_requests_post, requests_mock, caplog):
        requests_mock.post("https://compliance.passculture.team/latest/model/compliance/scoring", status_code=422)
        offer = offers_factories.OfferFactory(name="Hello la data")
        payload = compliance._get_payload_for_compliance_api(offer)

        with caplog.at_level(logging.ERROR):
            with pytest.raises(requests.ExternalAPIException) as exc:
                compliance.make_update_offer_compliance_score(payload)

        assert exc.value.is_retryable is False
        assert caplog.records[0].message == "Data sent to Compliance API is faulty"
        assert caplog.records[0].extra == {"status_code": 422}
        assert not db.session.query(offers_models.OfferCompliance).filter_by(offerId=offer.id).count()

    @mock.patch("pcapi.core.external.compliance.compliance_backend", ComplianceBackend())
    @mock.patch("pcapi.core.auth.api.get_id_token_from_google", return_value="Good token")
    def test_get_data_compliance_scoring_with_unknown_exception(self, mock_requests_post, requests_mock, caplog):
        requests_mock.post("https://compliance.passculture.team/latest/model/compliance/scoring", status_code=500)
        offer = offers_factories.OfferFactory(name="Hello la data")
        payload = compliance._get_payload_for_compliance_api(offer)

        with caplog.at_level(logging.ERROR):
            with pytest.raises(requests.ExternalAPIException) as exc:
                compliance.make_update_offer_compliance_score(payload)

        assert exc.value.is_retryable is True
        assert caplog.records[0].message == "Response from Compliance API is not ok"
        assert caplog.records[0].extra == {"status_code": 500}
        assert not db.session.query(offers_models.OfferCompliance).filter_by(offerId=offer.id).count()

    @pytest.mark.parametrize(
        "validation_status_prediction,validation_status_prediction_reason",
        (
            ("approved", "L'offre est conforme."),
            ("rejected", "L'offre n'est pas conforme car le prix du stock est trop élevé."),
        ),
    )
    @mock.patch("pcapi.core.external.compliance.compliance_backend", ComplianceBackend())
    @mock.patch("pcapi.core.auth.api.get_id_token_from_google", return_value="Good token")
    def test_get_data_compliance_validation_status_prediction(
        self,
        mock_get_id_token_from_google,
        requests_mock,
        validation_status_prediction,
        validation_status_prediction_reason,
    ):
        requests_mock.post(
            "https://compliance.passculture.team/latest/model/compliance/scoring",
            json={
                "probability_validated": 50,
                "rejection_main_features": ["stock_price", "offer_description"],
                "validation_status_prediction": validation_status_prediction,
                "validation_status_prediction_reason": validation_status_prediction_reason,
            },
        )
        offer = offers_factories.OfferFactory(name="Hello la data")
        payload = compliance._get_payload_for_compliance_api(offer)
        compliance.make_update_offer_compliance_score(payload)
        offer_compliance = db.session.query(offers_models.OfferCompliance).filter_by(offerId=offer.id).one()
        assert offer_compliance.validation_status_prediction == offers_models.ComplianceValidationStatusPrediction(
            validation_status_prediction
        )
        assert offer_compliance.validation_status_prediction_reason == validation_status_prediction_reason


@pytest.mark.usefixtures("db_session")
class GetPayloadForComplianceApiTest:
    def test_get_payload_for_compliance_api(self):
        offer = offers_factories.OfferFactory(
            name="Un vinyle de Taylor Swift",
            description="C'est une chanteuse, Taylor Swift",
            subcategoryId=subcategories.SUPPORT_PHYSIQUE_MUSIQUE_VINYLE.id,
            extraData={
                "author": "Taylor Swift",
                "performer": "Elizo Turner",
                "musicType": 870,
                "musicSubType": 876,
            },
        )
        expensive_stock = offers_factories.StockFactory(offer=offer, price=30)
        offers_factories.StockFactory(offer=offer, price=20)
        mediation = offers_factories.MediationFactory(offer=offer)

        offer_in_db = (
            db.session.query(offers_models.Offer)
            .filter(offers_models.Offer.id == offer.id)
            .options(sa_orm.joinedload(offers_models.Offer.stocks), sa_orm.joinedload(offers_models.Offer.mediations))
            .one()
        )

        with assert_num_queries(0):  # everything is already loaded in the query
            payload = compliance._get_payload_for_compliance_api(offer_in_db)

        assert payload.offer_id == str(offer.id)
        assert payload.offer_name == "Un vinyle de Taylor Swift"
        assert payload.offer_description == "C'est une chanteuse, Taylor Swift"
        assert payload.offer_subcategory_id == "SUPPORT_PHYSIQUE_MUSIQUE_VINYLE"
        assert payload.rayon is None
        assert payload.macro_rayon is None
        assert payload.stock_price == expensive_stock.price
        assert payload.image_url == mediation.thumbUrl
        assert payload.offer_type_label == "Country"
        assert payload.offer_sub_type_label == "Country Pop"
        assert payload.author == "Taylor Swift"
        assert payload.performer == "Elizo Turner"
