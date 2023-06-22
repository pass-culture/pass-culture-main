import logging

from flask import url_for
import pytest

from pcapi.core.educational import factories as educational_factories
from pcapi.core.educational import models as educational_models
import pcapi.core.educational.testing as adage_api_testing
import pcapi.core.educational.utils as educational_utils


pytestmark = pytest.mark.usefixtures("db_session")


class CreateCollectiveRequestTest:
    endpoint = "adage_iframe.create_collective_request"

    def test_post_collective_request(self, client, caplog):
        educational_institution = educational_factories.EducationalInstitutionFactory()
        educational_redactor = educational_factories.EducationalRedactorFactory()
        offer = educational_factories.CollectiveOfferTemplateFactory()

        body = {
            "phoneNumber": "0139980101",
            "totalStudents": 30,
            "totalTeachers": 2,
            "comment": "Un commentaire sublime que nous avons là",
        }

        # When
        client = client.with_adage_token(email=educational_redactor.email, uai=educational_institution.institutionId)
        with caplog.at_level(logging.INFO):
            response = client.post(url_for(self.endpoint, offer_id=offer.id), json=body)

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
        client = client.with_adage_token(email=educational_redactor.email, uai=educational_institution.institutionId)
        response = client.post(url_for(self.endpoint, offer_id=0), json=body)

        # Then
        assert response.status_code == 404
        assert response.json == {"code": "COLLECTIVE_OFFER_TEMPLATE_NOT_FOUND"}
        assert not adage_api_testing.adage_requests

    def test_post_collective_request_no_institution_found(self, client):
        educational_redactor = educational_factories.EducationalRedactorFactory(email="JamesHolden@rocinante.com")
        offer = educational_factories.CollectiveOfferTemplateFactory()

        body = {
            "email": "JamesHolden@rocinante.com",
            "phoneNumber": "0139980101",
            "totalStudents": 30,
            "totalTeachers": 2,
            "comment": "Un commentaire sublime que nous avons là",
        }

        # When
        client = client.with_adage_token(email=educational_redactor.email, uai="oh no, oh no, nonono")
        response = client.post(url_for(self.endpoint, offer_id=offer.id), json=body)

        # Then
        assert response.status_code == 404
        assert response.json == {"code": "INSTITUTION_NOT_FOUND"}
        assert not adage_api_testing.adage_requests

    def test_missing_redactor_is_created(self, client):
        """
        Test that if the redactor is missing from the database:
          1. it is created with its authenticated information;
          2. everything works as expected.
        """
        educational_institution = educational_factories.EducationalInstitutionFactory()
        educational_redactor = educational_factories.EducationalRedactorFactory.build()
        offer = educational_factories.CollectiveOfferTemplateFactory()

        body = {
            "phoneNumber": "0139980101",
            "totalStudents": 30,
            "totalTeachers": 2,
            "comment": "Un commentaire sublime que nous avons là",
        }

        client = client.with_adage_token(
            email=educational_redactor.email,
            civility=educational_redactor.civility,
            firstname=educational_redactor.firstName,
            lastname=educational_redactor.lastName,
            uai=educational_institution.institutionId,
        )

        response = client.post(url_for(self.endpoint, offer_id=offer.id), json=body)
        assert response.status_code == 200

        # quick checks: response and adage request
        assert response.json["email"] == educational_redactor.email
        assert len(adage_api_testing.adage_requests) == 1

        # check: a new redactor has been saved into database
        found_redactor = educational_models.EducationalRedactor.query.one()

        assert found_redactor.email == educational_redactor.email
        assert found_redactor.civility == educational_redactor.civility
        assert found_redactor.firstName == educational_redactor.firstName
        assert found_redactor.lastName == educational_redactor.lastName
