import pytest

from pcapi.core.offerers.factories import ApiKeyFactory
import pcapi.core.offerers.models
import pcapi.core.offers.factories as offers_factories
import pcapi.core.users.factories as users_factories
from pcapi.model_creators.generic_creators import create_bank_information
from pcapi.utils.date import format_into_utc_date
from pcapi.utils.human_ids import humanize

from tests.conftest import TestClient


class Returns404Test:
    @pytest.mark.usefixtures("db_session")
    def test_when_user_offerer_does_not_exist(self, app):
        # Given
        pro = users_factories.ProFactory()
        invalid_id = 12

        # When
        response = TestClient(app.test_client()).with_auth(pro.email).get("/offerers/%s" % invalid_id)

        # then
        assert response.status_code == 404
        assert response.json["global"] == ["La page que vous recherchez n'existe pas"]


class Returns200Test:
    @pytest.mark.usefixtures("db_session")
    def test_when_user_has_rights_on_offerer(self, app):
        # given

        pro = users_factories.ProFactory()
        offerer = offers_factories.OffererFactory()
        offers_factories.UserOffererFactory(user=pro, offerer=offerer)
        venue = offers_factories.VenueFactory(managingOfferer=offerer, withdrawalDetails="Venue withdrawal details")
        ApiKeyFactory(offerer=offerer, prefix="testenv_prefix")
        ApiKeyFactory(offerer=offerer, prefix="testenv_prefix2")

        offerer_bank_information = create_bank_information(offerer=offerer)
        venue_bank_information = create_bank_information(venue=venue, application_id=2)
        offerer = pcapi.core.offerers.models.Offerer.query.filter_by(id=offerer.id).first()

        # when
        response = TestClient(app.test_client()).with_auth(pro.email).get(f"/offerers/{humanize(offerer.id)}")

        expected_serialized_offerer = {
            "address": offerer.address,
            "apiKey": {"maxAllowed": 5, "prefixes": ["testenv_prefix", "testenv_prefix2"]},
            "bic": offerer_bank_information.bic,
            "iban": offerer_bank_information.iban,
            "city": offerer.city,
            "dateCreated": format_into_utc_date(offerer.dateCreated),
            "dateModifiedAtLastProvider": format_into_utc_date(offerer.dateModifiedAtLastProvider),
            "demarchesSimplifieesApplicationId": str(offerer.demarchesSimplifieesApplicationId),
            "fieldsUpdated": offerer.fieldsUpdated,
            "id": humanize(offerer.id),
            "idAtProviders": offerer.idAtProviders,
            "isValidated": offerer.isValidated,
            "lastProviderId": offerer.lastProviderId,
            "managedVenues": [
                {
                    "bic": venue_bank_information.bic,
                    "iban": venue_bank_information.iban,
                    "demarchesSimplifieesApplicationId": str(venue.demarchesSimplifieesApplicationId),
                    "address": offererVenue.address,
                    "bookingEmail": offererVenue.bookingEmail,
                    "city": offererVenue.city,
                    "comment": offererVenue.comment,
                    "dateCreated": format_into_utc_date(offererVenue.dateCreated),
                    "dateModifiedAtLastProvider": format_into_utc_date(offererVenue.dateModifiedAtLastProvider),
                    "departementCode": offererVenue.departementCode,
                    "id": humanize(offererVenue.id),
                    "idAtProviders": offererVenue.idAtProviders,
                    "isValidated": offererVenue.isValidated,
                    "isVirtual": offererVenue.isVirtual,
                    "lastProviderId": offererVenue.lastProviderId,
                    "latitude": float(offererVenue.latitude),
                    "longitude": float(offererVenue.longitude),
                    "managingOffererId": humanize(offererVenue.managingOffererId),
                    "name": offererVenue.name,
                    "nOffers": offererVenue.nOffers,
                    "postalCode": offererVenue.postalCode,
                    "publicName": offererVenue.publicName,
                    "siret": offererVenue.siret,
                    "stats": None,
                    "venueLabelId": humanize(offererVenue.venueLabelId),
                    "venueTypeId": humanize(offererVenue.venueTypeId),
                    "withdrawalDetails": venue.withdrawalDetails,
                }
                for offererVenue in offerer.managedVenues
            ],
            "name": offerer.name,
            "nOffers": offerer.nOffers,
            "postalCode": offerer.postalCode,
            "siren": offerer.siren,
        }

        # then
        assert response.status_code == 200
        assert response.json == expected_serialized_offerer
