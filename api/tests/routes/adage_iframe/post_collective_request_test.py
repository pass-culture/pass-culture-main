from datetime import datetime
import logging

import pytest

from pcapi.core.educational import factories as educational_factories
import pcapi.core.educational.testing as adage_api_testing
import pcapi.core.educational.utils as educational_utils


pytestmark = pytest.mark.usefixtures("db_session")

stock_date = datetime(2021, 5, 15)
educational_year_dates = {"start": datetime(2020, 9, 1), "end": datetime(2021, 8, 31)}


class Returns200Test:
    def test_post_collective_request(self, client, caplog):
        educational_institution = educational_factories.EducationalInstitutionFactory()
        educational_redactor = educational_factories.EducationalRedactorFactory()
        offer = educational_factories.CollectiveOfferTemplateFactory()
        offer_id = offer.id

        body = {
            "phoneNumber": "0139980101",
            "totalStudents": 30,
            "totalTeachers": 2,
            "comment": "Un commentaire sublime que nous avons là",
        }

        # When
        with caplog.at_level(logging.INFO):
            test_client = client.with_adage_token(
                email=educational_redactor.email, uai=educational_institution.institutionId
            )
            response = test_client.post(f"/adage-iframe/collective/offers-template/{offer_id}/request", json=body)

        # Then
        assert response.status_code == 200
        assert response.json["email"] == educational_redactor.email
        assert response.json["phoneNumber"] == "+33139980101"
        assert response.json["requestedDate"] is None
        assert response.json["totalStudents"] == 30
        assert response.json["totalTeachers"] == 2
        assert response.json["comment"] == "Un commentaire sublime que nous avons là"

        record = next(log for log in caplog.records if log.message == "CreateCollectiveOfferRequest")
        assert record.extra == {
            "id": response.json["id"],
            "collective_offer_template_id": offer.id,
            "requested_date": None,
            "total_students": body["totalStudents"],
            "total_teachers": body["totalTeachers"],
            "comment": body["comment"],
            "analyticsSource": "adage",
            "userId": educational_utils.get_hashed_user_id(educational_redactor.email),
        }

        assert len(adage_api_testing.adage_requests) == 1
        request = adage_api_testing.adage_requests[0]["sent_data"]
        assert request.redactorEmail == educational_redactor.email
        assert request.requestPhoneNumber == "+33139980101"
        assert request.totalStudents == 30
        assert request.totalTeachers == 2
        assert request.offerContactEmail == "collectiveofferfactory+contact@example.com"
        assert request.offerContactPhoneNumber == "+33199006328"
        assert request.offererName == offer.venue.managingOfferer.name
        assert request.venueName == offer.venue.name
        assert request.offerName == offer.name
        assert request.comment == body["comment"]
        assert not request.requestedDate


class Returns404Test:
    def test_post_collective_request_no_offer_template(self, client):
        educational_institution = educational_factories.EducationalInstitutionFactory()
        educational_redactor = educational_factories.EducationalRedactorFactory(email="JamesHolden@rocinante.com")

        body = {
            "email": "JamesHolden@rocinante.com",
            "phoneNumber": "0139980101",
            "totalStudents": 30,
            "totalTeachers": 2,
            "comment": "Un commentaire sublime que nous avons là",
        }

        # When
        test_client = client.with_adage_token(
            email=educational_redactor.email, uai=educational_institution.institutionId
        )
        response = test_client.post("/adage-iframe/collective/offers-template/0/request", json=body)

        # Then
        assert response.status_code == 404
        assert response.json == {"code": "COLLECTIVE_OFFER_TEMPLATE_NOT_FOUND"}
        assert not adage_api_testing.adage_requests

    def test_post_collective_request_no_institution_found(self, client):
        educational_redactor = educational_factories.EducationalRedactorFactory(email="JamesHolden@rocinante.com")
        offer = educational_factories.CollectiveOfferTemplateFactory()
        offer_id = offer.id

        body = {
            "email": "JamesHolden@rocinante.com",
            "phoneNumber": "0139980101",
            "totalStudents": 30,
            "totalTeachers": 2,
            "comment": "Un commentaire sublime que nous avons là",
        }

        # When
        test_client = client.with_adage_token(email=educational_redactor.email, uai="oh no, oh no, nonono")
        response = test_client.post(f"/adage-iframe/collective/offers-template/{offer_id}/request", json=body)

        # Then
        assert response.status_code == 404
        assert response.json == {"code": "INSTITUTION_NOT_FOUND"}
        assert not adage_api_testing.adage_requests
