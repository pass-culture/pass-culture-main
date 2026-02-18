import logging

import pytest
from flask import url_for

from pcapi.core.educational import factories
from pcapi.core.educational import models
from pcapi.core.educational import testing
from pcapi.core.educational import utils
from pcapi.models import db


pytestmark = pytest.mark.usefixtures("db_session")


def base_body():
    return {
        "phoneNumber": "0139980101",
        "totalStudents": 30,
        "totalTeachers": 2,
        "comment": "Un commentaire sublime que nous avons là",
    }


class CreateCollectiveRequestTest:
    endpoint = "adage_iframe.create_collective_request"

    def test_post_collective_request(self, client, caplog):
        educational_institution = factories.EducationalInstitutionFactory()
        educational_redactor = factories.EducationalRedactorFactory()
        offer = factories.CollectiveOfferTemplateFactory()

        body = base_body()
        client = client.with_adage_token(email=educational_redactor.email, uai=educational_institution.institutionId)
        with caplog.at_level(logging.INFO):
            response = client.post(url_for(self.endpoint, offer_id=offer.id), json=body)

        assert response.status_code == 201
        request_id = response.json["id"]

        collective_request = db.session.query(models.CollectiveOfferRequest).filter_by(id=request_id).one()
        assert collective_request.phoneNumber == "+33139980101"
        assert collective_request.requestedDate is None
        assert collective_request.totalStudents == 30
        assert collective_request.totalTeachers == 2
        assert collective_request.comment == "Un commentaire sublime que nous avons là"

        record = next(log for log in caplog.records if log.message == "CreateCollectiveOfferRequest")
        assert record.extra == {
            "id": response.json["id"],
            "collective_offer_template_id": offer.id,
            "requested_date": None,
            "total_students": body["totalStudents"],
            "total_teachers": body["totalTeachers"],
            "comment": body["comment"],
            "analyticsSource": "adage",
            "userId": utils.get_hashed_user_id(educational_redactor.email),
            "uai": educational_institution.institutionId,
            "user_role": models.AdageFrontRoles.REDACTOR,
        }

        assert len(testing.adage_requests) == 1
        request = testing.adage_requests[0]["sent_data"]
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
        educational_institution = factories.EducationalInstitutionFactory()
        educational_redactor = factories.EducationalRedactorFactory(email="JamesHolden@rocinante.com")

        unknown_template_id = 0
        client = client.with_adage_token(email=educational_redactor.email, uai=educational_institution.institutionId)
        response = client.post(url_for(self.endpoint, offer_id=unknown_template_id), json=base_body())

        assert response.status_code == 404
        assert response.json == {"code": "COLLECTIVE_OFFER_TEMPLATE_NOT_FOUND"}

    def test_post_collective_request_no_institution_found(self, client):
        educational_redactor = factories.EducationalRedactorFactory(email="JamesHolden@rocinante.com")
        offer = factories.CollectiveOfferTemplateFactory()

        unknown_uai = "unknown"
        client = client.with_adage_token(email=educational_redactor.email, uai=unknown_uai)
        response = client.post(url_for(self.endpoint, offer_id=offer.id), json=base_body())

        assert response.status_code == 404
        assert response.json == {"code": "INSTITUTION_NOT_FOUND"}
        assert not testing.adage_requests

    def test_missing_redactor_is_created(self, client):
        """
        Test that if the redactor is missing from the database:
          1. it is created with its authenticated information;
          2. everything works as expected.
        """
        educational_institution = factories.EducationalInstitutionFactory()
        educational_redactor = factories.EducationalRedactorFactory()
        offer = factories.CollectiveOfferTemplateFactory()

        client = client.with_adage_token(
            email=educational_redactor.email,
            civility=educational_redactor.civility,
            firstname=educational_redactor.firstName,
            lastname=educational_redactor.lastName,
            uai=educational_institution.institutionId,
        )

        response = client.post(url_for(self.endpoint, offer_id=offer.id), json=base_body())
        assert response.status_code == 201

        # quick checks: response and adage request
        request_id = response.json["id"]
        collective_request = db.session.query(models.CollectiveOfferRequest).filter_by(id=request_id).one()
        assert collective_request.educationalRedactorId == educational_redactor.id
        assert len(testing.adage_requests) == 1

        # check: a new redactor has been saved into database
        found_redactor = db.session.query(models.EducationalRedactor).one()

        assert found_redactor.email == educational_redactor.email
        assert found_redactor.civility == educational_redactor.civility
        assert found_redactor.firstName == educational_redactor.firstName
        assert found_redactor.lastName == educational_redactor.lastName

    def test_invalid_phone_number(self, client):
        educational_institution = factories.EducationalInstitutionFactory()
        educational_redactor = factories.EducationalRedactorFactory()
        offer = factories.CollectiveOfferTemplateFactory()

        body = {**base_body(), "phoneNumber": "0000000000000000"}

        client = client.with_adage_token(email=educational_redactor.email, uai=educational_institution.institutionId)
        response = client.post(url_for(self.endpoint, offer_id=offer.id), json=body)

        assert response.status_code == 400
        assert "phoneNumber" in response.json
