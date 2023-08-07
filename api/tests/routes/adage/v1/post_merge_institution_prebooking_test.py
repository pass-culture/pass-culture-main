from unittest.mock import patch

import pytest

from pcapi.core.educational import factories as educational_factories
from pcapi.core.educational import repository as educational_repository


@pytest.mark.usefixtures("db_session")
class PostMergeInstitutionPrebookingTest:
    def test_merge_institution_prebooking(self, client) -> None:
        institution_source, institution_destination = educational_factories.EducationalInstitutionFactory.create_batch(
            2
        )
        booking_1, booking_2, booking_3 = educational_factories.CollectiveBookingFactory.create_batch(
            3, educationalInstitution=institution_source
        )
        offer_1, offer_2 = educational_factories.CollectiveOfferFactory.create_batch(2, institution=institution_source)
        educational_factories.CollectiveStockFactory(
            collectiveOffer=offer_1,
            collectiveBookings=[booking_1],
        )
        educational_factories.CollectiveStockFactory(
            collectiveOffer=offer_2,
            collectiveBookings=[booking_2],
        )

        body = {
            "source_uai": institution_source.institutionId,
            "destination_uai": institution_destination.institutionId,
            "bookings_ids": [booking_1.id, booking_2.id, booking_3.id],
        }

        client = client.with_eac_token()
        response = client.post("/adage/v1/prebookings/move", json=body)

        assert response.status_code == 204
        assert booking_1.educationalInstitution.institutionId == institution_destination.institutionId
        assert booking_2.educationalInstitution.institutionId == institution_destination.institutionId
        assert booking_3.educationalInstitution.institutionId == institution_destination.institutionId
        assert offer_1.institution == institution_destination
        assert offer_2.institution == institution_destination

    def test_merge_institution_prebooking_institution_destination_in_adage_only(self, client) -> None:
        institution_source = educational_factories.EducationalInstitutionFactory()
        booking_1, booking_2 = educational_factories.CollectiveBookingFactory.create_batch(
            2, educationalInstitution=institution_source
        )
        offer_1, offer_2 = educational_factories.CollectiveOfferFactory.create_batch(2, institution=institution_source)
        educational_factories.CollectiveStockFactory(
            collectiveOffer=offer_1,
            collectiveBookings=[booking_1],
        )
        educational_factories.CollectiveStockFactory(
            collectiveOffer=offer_2,
            collectiveBookings=[booking_2],
        )

        body = {
            "source_uai": institution_source.institutionId,
            "destination_uai": "0470009E",
            "bookings_ids": [booking_1.id, booking_2.id],
        }

        client = client.with_eac_token()
        with patch("pcapi.core.educational.adage_backends.get_adage_educational_institutions"):
            response = client.post("/adage/v1/prebookings/move", json=body)

        assert response.status_code == 204
        institution_destination = educational_repository.find_educational_institution_by_uai_code(
            body["destination_uai"]
        )
        assert booking_1.educationalInstitution.institutionId == institution_destination.institutionId
        assert booking_2.educationalInstitution.institutionId == institution_destination.institutionId
        assert offer_1.institution == institution_destination
        assert offer_2.institution == institution_destination

    def test_merge_institution_prebooking_institution_destination_dont_exist(self, client) -> None:
        institution_source = educational_factories.EducationalInstitutionFactory()

        body = {
            "source_uai": institution_source.institutionId,
            "destination_uai": "oh no",
            "bookings_ids": [1, 2, 3],
        }

        client = client.with_eac_token()
        with patch("pcapi.core.educational.adage_backends.get_adage_educational_institutions"):
            response = client.post("/adage/v1/prebookings/move", json=body)

        assert response.status_code == 404
        assert response.json == {"destination_uai": "not found"}

    def test_merge_institution_prebooking_institution_source_not_found(self, client) -> None:
        body = {
            "source_uai": "oh no nono nonono",
            "destination_uai": "the destination",
            "bookings_ids": [1, 2, 3],
        }

        client = client.with_eac_token()
        response = client.post("/adage/v1/prebookings/move", json=body)

        assert response.status_code == 404
        assert response.json == {"code": "Source institution not found"}

    def test_merge_institution_prebooking_institution_authentification_failed(self, client) -> None:
        body = {
            "source_uai": "1",
            "destination_uai": "2",
            "bookings_ids": [1],
        }

        response = client.post("/adage/v1/prebookings/move", json=body)

        assert response.status_code == 403
        assert response.json == {"Authorization": ["Wrong api key"]}
