import pytest

import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offers.factories as offers_factories
import pcapi.core.users.factories as users_factories
from pcapi.utils.date import format_into_utc_date
from pcapi.utils.human_ids import humanize

from tests.conftest import TestClient


class Returns200Test:
    # if bannerMeta is not None, the response should only serialize some
    # fields, others should be ignored.
    @pytest.mark.parametrize(
        "banner_meta_in,banner_meta_out",
        [
            ({"image_credit": "someone"}, {"image_credit": "someone"}),
            ({"random": "content", "should": "be_ignored"}, {}),
            (None, None),
        ],
    )
    @pytest.mark.usefixtures("db_session")
    def when_user_has_rights_on_managing_offerer(self, client, banner_meta_in, banner_meta_out):
        # given
        user_offerer = offerers_factories.UserOffererFactory(user__email="user.pro@test.com")
        venue = offerers_factories.VenueFactory(
            name="L'encre et la plume", managingOfferer=user_offerer.offerer, bannerMeta=banner_meta_in
        )
        bank_information = offers_factories.BankInformationFactory(venue=venue)

        expected_serialized_venue = {
            "address": venue.address,
            "audioDisabilityCompliant": venue.audioDisabilityCompliant,
            "bic": bank_information.bic,
            "bookingEmail": venue.bookingEmail,
            "businessUnit": {
                "bic": venue.businessUnit.bankAccount.bic,
                "iban": venue.businessUnit.bankAccount.iban,
                "id": venue.businessUnit.id,
                "name": venue.businessUnit.name,
                "siret": venue.businessUnit.siret,
            },
            "businessUnitId": venue.businessUnitId,
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
            "demarchesSimplifieesApplicationId": venue.demarchesSimplifieesApplicationId,
            "departementCode": venue.departementCode,
            "description": venue.description,
            "fieldsUpdated": venue.fieldsUpdated,
            "iban": bank_information.iban,
            "id": humanize(venue.id),
            "idAtProviders": venue.idAtProviders,
            "isBusinessUnitMainVenue": True,
            "isPermanent": venue.isPermanent,
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
            "mentalDisabilityCompliant": venue.mentalDisabilityCompliant,
            "motorDisabilityCompliant": venue.motorDisabilityCompliant,
            "name": venue.name,
            "postalCode": venue.postalCode,
            "publicName": venue.publicName,
            "siret": venue.siret,
            "venueLabelId": humanize(venue.venueLabelId),
            "venueTypeCode": venue.venueTypeCode.name if venue.venueTypeCode else None,
            "visualDisabilityCompliant": venue.visualDisabilityCompliant,
            "withdrawalDetails": None,
            "bannerUrl": venue.bannerUrl,
            "bannerMeta": banner_meta_out,
            "nonHumanizedId": venue.id,
        }

        # when
        auth_request = client.with_session_auth(email=user_offerer.user.email)
        response = auth_request.get("/venues/%s" % humanize(venue.id))

        # then
        assert response.status_code == 200
        assert response.json == expected_serialized_venue


class Returns403Test:
    @pytest.mark.usefixtures("db_session")
    def when_current_user_doesnt_have_rights(self, app):
        # given
        pro = users_factories.ProFactory(email="user.pro@example.com")
        venue = offerers_factories.VenueFactory(name="L'encre et la plume")

        # when
        auth_request = TestClient(app.test_client()).with_session_auth(email=pro.email)
        response = auth_request.get("/venues/%s" % humanize(venue.id))

        # then
        assert response.status_code == 403
        assert response.json["global"] == [
            "Vous n'avez pas les droits d'accès suffisant pour accéder à cette information."
        ]
