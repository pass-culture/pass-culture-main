import pytest

from pcapi.core.educational import models
from pcapi.core.educational.factories import CancelledCollectiveBookingFactory
from pcapi.core.educational.factories import CollectiveBookingFactory
from pcapi.core.educational.factories import EducationalInstitutionFactory
from pcapi.core.educational.factories import EducationalRedactorFactory
from pcapi.core.educational.factories import EducationalYearFactory
from pcapi.core.testing import assert_num_queries

from tests.routes.adage.v1.conftest import expected_serialized_prebooking


@pytest.mark.usefixtures("db_session")
class Returns200Test:
    num_queries = 1  # fetch bookings
    num_queries += 1  # fetch FF (WIP_ENABLE_OFFER_ADDRESS_COLLECTIVE)

    def test_get_prebookings_without_query_params(self, client):
        redactor = EducationalRedactorFactory(
            civility="M.",
            firstName="Jean",
            lastName="Doudou",
            email="jean.doux@example.com",
        )
        educationalYear = EducationalYearFactory()
        educationalInstitution = EducationalInstitutionFactory()
        booking = CollectiveBookingFactory(
            educationalYear=educationalYear,
            educationalInstitution=educationalInstitution,
            educationalRedactor=redactor,
            collectiveStock__collectiveOffer__description=None,
            collectiveStock__collectiveOffer__students=[
                models.StudentLevels.CAP1,
                models.StudentLevels.CAP2,
                models.StudentLevels.GENERAL2,
                models.StudentLevels.GENERAL1,
            ],
            collectiveStock__collectiveOffer__offerVenue={
                "addressType": "other",
                "otherAddress": "1 rue des polissons, Paris 75017",
                "venueId": "",
            },
            collectiveStock__collectiveOffer__locationType=models.CollectiveLocationType.TO_BE_DEFINED,
            collectiveStock__collectiveOffer__contactEmail="miss.rond@point.com",
            collectiveStock__collectiveOffer__contactPhone="0101010101",
            collectiveStock__collectiveOffer__audioDisabilityCompliant=True,
            collectiveStock__collectiveOffer__visualDisabilityCompliant=True,
        )
        other_educational_year = EducationalYearFactory(adageId="adageId")
        other_educational_institution = EducationalInstitutionFactory(institutionId="institutionId")
        CollectiveBookingFactory(educationalYear=other_educational_year)
        CollectiveBookingFactory(educationalInstitution=other_educational_institution)

        dst = f"/adage/v1/years/{booking.educationalYear.adageId}/educational_institution/{booking.educationalInstitution.institutionId}/prebookings"

        with assert_num_queries(self.num_queries):
            response = client.with_eac_token().get(dst)

        assert response.status_code == 200
        assert "prebookings" in response.json.keys()
        assert len(response.json["prebookings"]) == 1
        assert response.json["prebookings"][0] == expected_serialized_prebooking(booking)

    def test_get_prebookings_with_query_params(self, client):
        redactor = EducationalRedactorFactory(
            civility="M.",
            firstName="Jean",
            lastName="Doudou",
            email="jean.doux@example.com",
        )
        another_redactor = EducationalRedactorFactory(
            civility="Mme.",
            firstName="Jeanne",
            lastName="Dodu",
            email="jeanne.dodu@example.com",
        )
        educationalYear = EducationalYearFactory()
        educationalInstitution = EducationalInstitutionFactory()
        CollectiveBookingFactory(
            educationalRedactor=another_redactor,
            educationalYear=educationalYear,
            educationalInstitution=educationalInstitution,
            status="PENDING",
        )
        booking = CollectiveBookingFactory(
            educationalRedactor=redactor,
            educationalYear=educationalYear,
            educationalInstitution=educationalInstitution,
            status="PENDING",
        )

        dst = f"/adage/v1/years/{booking.educationalYear.adageId}/educational_institution/{booking.educationalInstitution.institutionId}/prebookings?redactorEmail={redactor.email}"

        with assert_num_queries(self.num_queries):
            response = client.with_eac_token().get(dst)

        assert response.status_code == 200
        assert response.json == {"prebookings": [expected_serialized_prebooking(booking)]}

    def test_get_prebookings_with_cancellation_reason(self, client):
        redactor = EducationalRedactorFactory(
            civility="M.",
            firstName="Jean",
            lastName="Doudou",
            email="jean.doux@example.com",
        )
        educationalYear = EducationalYearFactory()
        educationalInstitution = EducationalInstitutionFactory()
        booking = CancelledCollectiveBookingFactory(
            cancellationReason=models.CollectiveBookingCancellationReasons.BACKOFFICE,
            educationalYear=educationalYear,
            educationalInstitution=educationalInstitution,
            educationalRedactor=redactor,
        )

        dst = f"/adage/v1/years/{booking.educationalYear.adageId}/educational_institution/{booking.educationalInstitution.institutionId}/prebookings"

        with assert_num_queries(self.num_queries):
            response = client.with_eac_token().get(dst)

        assert response.status_code == 200
        assert len(response.json["prebookings"]) == 1
        assert response.json["prebookings"][0]["cancellationReason"] == "BACKOFFICE"

    @pytest.mark.features(WIP_ENABLE_OFFER_ADDRESS_COLLECTIVE=True)
    def test_get_prebookings_with_oa(self, client):
        booking = CollectiveBookingFactory(
            educationalYear=EducationalYearFactory(),
            educationalInstitution=EducationalInstitutionFactory(),
            collectiveStock__collectiveOffer__locationType=models.CollectiveLocationType.ADDRESS,
            collectiveStock__collectiveOffer__offererAddress=None,
            collectiveStock__collectiveOffer__locationComment=None,
        )
        offer = booking.collectiveStock.collectiveOffer
        offer.offererAddress = offer.venue.offererAddress

        dst = f"/adage/v1/years/{booking.educationalYear.adageId}/educational_institution/{booking.educationalInstitution.institutionId}/prebookings"
        with assert_num_queries(self.num_queries):
            response = client.with_eac_token().get(dst)

        assert response.status_code == 200
        assert response.json == {
            "prebookings": [
                {
                    **expected_serialized_prebooking(booking),
                    "address": offer.offererAddress.address.fullAddress,
                }
            ]
        }
