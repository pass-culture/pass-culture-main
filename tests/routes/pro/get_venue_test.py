import pytest

import pcapi.core.offers.factories as offers_factories
import pcapi.core.users.factories as users_factories
from pcapi.utils.date import format_into_utc_date
from pcapi.utils.human_ids import humanize

from tests.conftest import TestClient


class Returns200Test:
    @pytest.mark.usefixtures("db_session")
    def when_user_has_rights_on_managing_offerer(self, app):
        # given
        user_offerer = offers_factories.UserOffererFactory(user__email="user.pro@test.com")
        venue = offers_factories.VenueFactory(name="L'encre et la plume", managingOfferer=user_offerer.offerer)
        bank_information = offers_factories.BankInformationFactory(venue=venue)

        expected_serialized_venue = {
            "address": venue.address,
            "bic": bank_information.bic,
            "bookingEmail": venue.bookingEmail,
            "city": venue.city,
            "contact": {
                "email": venue.contact.email,
                "website": venue.contact.website,
                "phoneNumber": venue.contact.phone_number,
                "socialMedias": venue.contact.social_medias,
            },
            "comment": venue.comment,
            "dateCreated": format_into_utc_date(venue.dateCreated),
            "dateModifiedAtLastProvider": format_into_utc_date(venue.dateModifiedAtLastProvider),
            "demarchesSimplifieesApplicationId": str(venue.demarchesSimplifieesApplicationId),
            "departementCode": venue.departementCode,
            "fieldsUpdated": venue.fieldsUpdated,
            "iban": bank_information.iban,
            "id": humanize(venue.id),
            "idAtProviders": venue.idAtProviders,
            "isValidated": venue.isValidated,
            "isVirtual": venue.isVirtual,
            "latitude": float(venue.latitude),
            "lastProviderId": venue.lastProviderId,
            "longitude": float(venue.longitude),
            "managingOfferer": {
                "address": venue.managingOfferer.address,
                "bic": venue.managingOfferer.bic,
                "city": venue.managingOfferer.city,
                "dateCreated": format_into_utc_date(venue.managingOfferer.dateCreated),
                "dateModifiedAtLastProvider": format_into_utc_date(venue.managingOfferer.dateModifiedAtLastProvider),
                "demarchesSimplifieesApplicationId": venue.managingOfferer.demarchesSimplifieesApplicationId,
                "fieldsUpdated": venue.managingOfferer.fieldsUpdated,
                "iban": venue.managingOfferer.iban,
                "id": humanize(venue.managingOfferer.id),
                "idAtProviders": venue.managingOfferer.idAtProviders,
                "isValidated": venue.managingOfferer.isValidated,
                "lastProviderId": venue.managingOfferer.lastProviderId,
                "name": venue.managingOfferer.name,
                "postalCode": venue.managingOfferer.postalCode,
                "siren": venue.managingOfferer.siren,
            },
            "managingOffererId": humanize(venue.managingOffererId),
            "name": venue.name,
            "postalCode": venue.postalCode,
            "publicName": venue.publicName,
            "siret": venue.siret,
            "venueLabelId": humanize(venue.venueLabelId),
            "venueTypeId": humanize(venue.venueTypeId),
            "withdrawalDetails": None,
        }

        # when
        auth_request = TestClient(app.test_client()).with_auth(email=user_offerer.user.email)
        response = auth_request.get("/venues/%s" % humanize(venue.id))

        # then
        assert response.status_code == 200
        assert response.json == expected_serialized_venue


class Returns403Test:
    @pytest.mark.usefixtures("db_session")
    def when_current_user_doesnt_have_rights(self, app):
        # given
        pro = users_factories.ProFactory(email="user.pro@example.com")
        venue = offers_factories.VenueFactory(name="L'encre et la plume")

        # when
        auth_request = TestClient(app.test_client()).with_auth(email=pro.email)
        response = auth_request.get("/venues/%s" % humanize(venue.id))

        # then
        assert response.status_code == 403
        assert response.json["global"] == [
            "Vous n'avez pas les droits d'accès suffisant pour accéder à cette information."
        ]
