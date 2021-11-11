import pytest

from pcapi.core import testing
from pcapi.core.offerers.factories import ApiKeyFactory
import pcapi.core.offers.factories as offers_factories
import pcapi.core.users.factories as users_factories
from pcapi.utils.date import format_into_utc_date
from pcapi.utils.human_ids import humanize

from tests.conftest import TestClient


class Returns404Test:
    @pytest.mark.usefixtures("db_session")
    def test_when_user_offerer_does_not_exist(self, app):
        pro = users_factories.ProFactory()
        invalid_id = 12

        response = TestClient(app.test_client()).with_session_auth(pro.email).get("/offerers/%s" % invalid_id)

        assert response.status_code == 404
        assert response.json["global"] == ["La page que vous recherchez n'existe pas"]


class Returns200Test:
    @pytest.mark.usefixtures("db_session")
    def test_when_user_has_rights_on_offerer(self, app):
        pro = users_factories.ProFactory()
        offerer = offers_factories.OffererFactory()
        offers_factories.UserOffererFactory(user=pro, offerer=offerer)
        venue_1 = offers_factories.VenueFactory(managingOfferer=offerer, withdrawalDetails="Venue withdrawal details")
        offers_factories.OfferFactory(venue=venue_1)
        venue_2 = offers_factories.VenueFactory(
            managingOfferer=offerer, withdrawalDetails="Other venue withdrawal details"
        )
        offers_factories.VenueFactory(managingOfferer=offerer, withdrawalDetails="More venue withdrawal details")
        ApiKeyFactory(offerer=offerer, prefix="testenv_prefix")
        ApiKeyFactory(offerer=offerer, prefix="testenv_prefix2")
        offers_factories.BankInformationFactory(venue=venue_1, applicationId=2, status="REJECTED")
        offers_factories.BankInformationFactory(venue=venue_1, applicationId=3)
        offers_factories.BankInformationFactory(venue=venue_2, applicationId=4)

        client = TestClient(app.test_client()).with_session_auth(pro.email)
        n_queries = (
            testing.AUTHENTICATION_QUERIES
            + 1  # check_user_has_access_to_offerer
            + 1  # Offerer api_key prefix
            + 1  # Offerer hasDigitalVenueAtLeastOneOffer
            + 1  # Offerer BankInformation
            + 1  # Offerer hasMissingBankInformation
        )
        with testing.assert_num_queries(n_queries):
            response = client.get(f"/offerers/{humanize(offerer.id)}")

        expected_serialized_offerer = {
            "address": offerer.address,
            "apiKey": {"maxAllowed": 5, "prefixes": ["testenv_prefix", "testenv_prefix2"]},
            "bic": None,
            "iban": None,
            "city": offerer.city,
            "dateCreated": format_into_utc_date(offerer.dateCreated),
            "dateModifiedAtLastProvider": format_into_utc_date(offerer.dateModifiedAtLastProvider),
            "demarchesSimplifieesApplicationId": None,
            "hasDigitalVenueAtLeastOneOffer": False,
            "fieldsUpdated": offerer.fieldsUpdated,
            "hasMissingBankInformation": True,
            "id": humanize(offerer.id),
            "idAtProviders": offerer.idAtProviders,
            "isValidated": offerer.isValidated,
            "lastProviderId": offerer.lastProviderId,
            "managedVenues": [
                {
                    "audioDisabilityCompliant": False,
                    "address": offererVenue.address,
                    "bookingEmail": offererVenue.bookingEmail,
                    "city": offererVenue.city,
                    "comment": offererVenue.comment,
                    "departementCode": offererVenue.departementCode,
                    "id": humanize(offererVenue.id),
                    "isValidated": offererVenue.isValidated,
                    "isVirtual": offererVenue.isVirtual,
                    "managingOffererId": humanize(offererVenue.managingOffererId),
                    "mentalDisabilityCompliant": False,
                    "motorDisabilityCompliant": False,
                    "name": offererVenue.name,
                    "postalCode": offererVenue.postalCode,
                    "publicName": offererVenue.publicName,
                    "venueLabelId": humanize(offererVenue.venueLabelId),
                    "venueTypeId": humanize(offererVenue.venueTypeId),
                    "visualDisabilityCompliant": False,
                    "withdrawalDetails": offererVenue.withdrawalDetails,
                }
                for offererVenue in offerer.managedVenues
            ],
            "name": offerer.name,
            "postalCode": offerer.postalCode,
            "siren": offerer.siren,
        }
        assert response.status_code == 200
        assert response.json == expected_serialized_offerer
