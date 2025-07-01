import pytest

from pcapi.core.educational import models
from pcapi.core.educational.factories import CollectiveBookingFactory
from pcapi.core.educational.factories import EducationalDepositFactory
from pcapi.core.educational.factories import EducationalInstitutionFactory
from pcapi.core.educational.factories import EducationalRedactorFactory
from pcapi.core.educational.factories import EducationalYearFactory
from pcapi.core.testing import assert_num_queries

from tests.routes.adage.v1.conftest import expected_serialized_prebooking


@pytest.mark.usefixtures("db_session")
class Returns200Test:
    def test_get_educational_institution(self, client):
        redactor = EducationalRedactorFactory(
            civility="M.",
            firstName="Jean",
            lastName="Doudou",
            email="jean.doux@example.com",
        )
        educational_year = EducationalYearFactory()
        educational_institution = EducationalInstitutionFactory()
        EducationalDepositFactory(
            educationalInstitution=educational_institution,
            educationalYear=educational_year,
            amount=2000,
            isFinal=True,
            creditRatio=0.255,
        )
        EducationalInstitutionFactory()
        booking = CollectiveBookingFactory(
            educationalRedactor=redactor,
            educationalYear=educational_year,
            educationalInstitution=educational_institution,
        )
        other_educational_year = EducationalYearFactory(adageId="toto")
        other_educational_institution = EducationalInstitutionFactory(institutionId="tata")
        CollectiveBookingFactory(educationalYear=other_educational_year)
        CollectiveBookingFactory(educationalInstitution=other_educational_institution)
        EducationalDepositFactory(
            educationalInstitution=educational_institution,
            educationalYear=other_educational_year,
            amount=2000,
            isFinal=False,
        )
        EducationalDepositFactory(
            educationalInstitution=other_educational_institution,
            educationalYear=educational_year,
            amount=2000,
            isFinal=False,
        )

        response = client.with_eac_token().get(
            f"/adage/v1/years/{educational_year.adageId}/educational_institution/{educational_institution.institutionId}"
        )

        assert response.status_code == 200
        assert response.json == {
            "credit": 2000,
            "creditRatio": 0.255,
            "isFinal": True,
            "prebookings": [expected_serialized_prebooking(booking)],
        }

    @pytest.mark.features(WIP_ENABLE_OFFER_ADDRESS_COLLECTIVE=True)
    def test_get_educational_institution_school(self, client):
        educational_year = EducationalYearFactory()
        educational_institution = EducationalInstitutionFactory()
        booking = CollectiveBookingFactory(
            educationalYear=educational_year,
            educationalInstitution=educational_institution,
            collectiveStock__collectiveOffer__locationType=models.CollectiveLocationType.SCHOOL,
            collectiveStock__collectiveOffer__offererAddress=None,
            collectiveStock__collectiveOffer__locationComment=None,
        )

        response = client.with_eac_token().get(
            f"/adage/v1/years/{educational_year.adageId}/educational_institution/{educational_institution.institutionId}"
        )

        assert response.status_code == 200
        assert response.json == {
            "credit": 0,
            "creditRatio": None,
            "isFinal": False,
            "prebookings": [{**expected_serialized_prebooking(booking), "address": "Dans l'établissement scolaire"}],
        }

    @pytest.mark.features(WIP_ENABLE_OFFER_ADDRESS_COLLECTIVE=True)
    def test_get_educational_institution_address(self, client):
        educational_year = EducationalYearFactory()
        educational_institution = EducationalInstitutionFactory()
        booking = CollectiveBookingFactory(
            educationalYear=educational_year,
            educationalInstitution=educational_institution,
            collectiveStock__collectiveOffer__locationType=models.CollectiveLocationType.ADDRESS,
            collectiveStock__collectiveOffer__offererAddress=None,
            collectiveStock__collectiveOffer__locationComment=None,
        )
        offer = booking.collectiveStock.collectiveOffer
        offer.offererAddress = offer.venue.offererAddress

        response = client.with_eac_token().get(
            f"/adage/v1/years/{educational_year.adageId}/educational_institution/{educational_institution.institutionId}"
        )

        assert response.status_code == 200
        assert response.json == {
            "credit": 0,
            "creditRatio": None,
            "isFinal": False,
            "prebookings": [
                {
                    **expected_serialized_prebooking(booking),
                    "address": offer.offererAddress.address.fullAddress,
                }
            ],
        }

    @pytest.mark.features(WIP_ENABLE_OFFER_ADDRESS_COLLECTIVE=True)
    def test_get_educational_institution_to_be_defined(self, client):
        educational_year = EducationalYearFactory()
        educational_institution = EducationalInstitutionFactory()
        booking = CollectiveBookingFactory(
            educationalYear=educational_year,
            educationalInstitution=educational_institution,
            collectiveStock__collectiveOffer__locationType=models.CollectiveLocationType.TO_BE_DEFINED,
            collectiveStock__collectiveOffer__offererAddress=None,
            collectiveStock__collectiveOffer__locationComment="Somewhere in Paris",
        )

        response = client.with_eac_token().get(
            f"/adage/v1/years/{educational_year.adageId}/educational_institution/{educational_institution.institutionId}"
        )

        assert response.status_code == 200
        assert response.json == {
            "credit": 0,
            "creditRatio": None,
            "isFinal": False,
            "prebookings": [{**expected_serialized_prebooking(booking), "address": "Somewhere in Paris"}],
        }

    def test_get_educational_institution_num_queries(self, client):
        redactor = EducationalRedactorFactory()
        educational_year = EducationalYearFactory()
        educational_institution = EducationalInstitutionFactory()
        EducationalDepositFactory(
            educationalInstitution=educational_institution,
            educationalYear=educational_year,
            amount=200000,
            isFinal=True,
        )
        EducationalInstitutionFactory()
        CollectiveBookingFactory.create_batch(
            10,
            educationalRedactor=redactor,
            educationalYear=educational_year,
            educationalInstitution=educational_institution,
        )
        other_educational_year = EducationalYearFactory(adageId="toto")
        other_educational_institution = EducationalInstitutionFactory(institutionId="tata")
        CollectiveBookingFactory(educationalYear=other_educational_year)
        CollectiveBookingFactory(educationalInstitution=other_educational_institution)
        EducationalDepositFactory(
            educationalInstitution=educational_institution,
            educationalYear=other_educational_year,
            amount=2000,
            isFinal=False,
        )
        EducationalDepositFactory(
            educationalInstitution=other_educational_institution,
            educationalYear=educational_year,
            amount=2000,
            isFinal=False,
        )

        adage_id = educational_year.adageId
        institution_id = educational_institution.institutionId

        dst = f"/adage/v1/years/{adage_id}/educational_institution/{institution_id}"

        num_queries = 1  # fetch the institution
        num_queries += 1  # fetch the prebookings
        num_queries += 1  # fetch the deposit
        num_queries += 1  # fetch FF (WIP_ENABLE_OFFER_ADDRESS_COLLECTIVE)
        with assert_num_queries(num_queries):
            client.with_eac_token().get(dst)

    def test_get_educational_institution_without_deposit(self, client):
        educational_year = EducationalYearFactory()
        educational_institution = EducationalInstitutionFactory()

        response = client.with_eac_token().get(
            f"/adage/v1/years/{educational_year.adageId}/educational_institution/{educational_institution.institutionId}"
        )

        assert response.status_code == 200
        assert response.json == {
            "credit": 0,
            "creditRatio": None,
            "isFinal": False,
            "prebookings": [],
        }


@pytest.mark.usefixtures("db_session")
class Returns404Test:
    def test_get_educational_institution_not_found(self, client):
        educational_year = EducationalYearFactory()
        EducationalInstitutionFactory()

        response = client.with_eac_token().get(
            f"/adage/v1/years/{educational_year.adageId}/educational_institution/UNKNOWN"
        )

        assert response.status_code == 404
        assert response.json == {"code": "EDUCATIONAL_INSTITUTION_NOT_FOUND"}
