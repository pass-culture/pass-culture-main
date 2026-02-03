from datetime import date
from datetime import timedelta

import pytest
from flask import url_for

import pcapi.core.educational.factories as educational_factories
import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.users.factories as users_factories
from pcapi.core import testing
from pcapi.core.testing import assert_num_queries


@pytest.mark.usefixtures("db_session")
class GetCollectiveOfferRequestTest:
    def test_get_offer_request(self, client):
        pro_user = users_factories.ProFactory()

        redactor = educational_factories.EducationalRedactorFactory()
        request = educational_factories.CollectiveOfferRequestFactory(
            educationalRedactor=redactor,
            requestedDate=date.today() + timedelta(days=7),
            totalStudents=40,
            totalTeachers=2,
            comment="Some offer request with all information filled",
            phoneNumber="0102030405",
            dateCreated=date.today(),
        )

        offerers_factories.UserOffererFactory(
            user=pro_user, offerer=request.collectiveOfferTemplate.venue.managingOfferer
        )

        dst = url_for(
            "Private API.get_collective_offer_request",
            offer_id=request.collectiveOfferTemplateId,
            request_id=request.id,
        )
        client = client.with_session_auth(email=pro_user.email)

        # fetch session + user (1 query)
        # fetch collective offer request and related data (1 query)
        # check whether user has access to offerer (1 query)
        with testing.assert_num_queries(3):
            response = client.get(dst)

        assert response.status_code == 200
        assert response.json == {
            "redactor": {
                "firstName": redactor.firstName,
                "lastName": redactor.lastName,
                "email": redactor.email,
            },
            "requestedDate": request.requestedDate.isoformat(),
            "totalStudents": request.totalStudents,
            "totalTeachers": request.totalTeachers,
            "comment": request.comment,
            "phoneNumber": request.phoneNumber,
            "dateCreated": request.dateCreated.isoformat(),
            "institution": {
                "institutionId": request.educationalInstitution.institutionId,
                "institutionType": request.educationalInstitution.institutionType,
                "name": request.educationalInstitution.name,
                "city": request.educationalInstitution.city,
                "postalCode": request.educationalInstitution.postalCode,
            },
        }

    def test_user_does_not_have_access_to_the_offer(self, client):
        pro_user = users_factories.ProFactory()
        another_pro_user = users_factories.ProFactory()

        redactor = educational_factories.EducationalRedactorFactory()
        request = educational_factories.CollectiveOfferRequestFactory(educationalRedactor=redactor)
        offerers_factories.UserOffererFactory(
            user=another_pro_user, offerer=request.collectiveOfferTemplate.venue.managingOfferer
        )

        dst = url_for(
            "Private API.get_collective_offer_request",
            offer_id=request.collectiveOfferTemplateId,
            request_id=request.id,
        )

        client = client.with_session_auth(email=pro_user.email)
        expected_num_queries = 5
        # session + user
        # collective_offer_request
        # user_offerer
        # rollback
        # rollback
        with assert_num_queries(expected_num_queries):
            response = client.get(dst)
            assert response.status_code == 403

    def test_offer_request_does_not_exist(self, client):
        pro_user = users_factories.ProFactory()
        request = educational_factories.CollectiveOfferRequestFactory()
        offerers_factories.UserOffererFactory(
            user=pro_user, offerer=request.collectiveOfferTemplate.venue.managingOfferer
        )

        dst = url_for(
            "Private API.get_collective_offer_request",
            offer_id=request.collectiveOfferTemplateId,
            request_id=request.id + 1,
        )

        client = client.with_session_auth(email=pro_user.email)
        with assert_num_queries(4):  #  session + collective_offer_request + rollback + rollback
            response = client.get(dst)
            assert response.status_code == 404
