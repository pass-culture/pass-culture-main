import datetime

import pytest

from pcapi.core import testing
import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offers.factories as offers_factories
import pcapi.core.users.factories as users_factories
from pcapi.models import db
from pcapi.utils.date import format_into_utc_date
from pcapi.utils.human_ids import humanize
from pcapi.utils.image_conversion import DO_NOT_CROP

from tests.conftest import TestClient


@pytest.mark.usefixtures("db_session")
class Returns200Test:
    def when_user_has_rights_on_managing_offerer(self, client):
        now = datetime.datetime.utcnow()
        user_offerer = offerers_factories.UserOffererFactory(user__email="user.pro@test.com")
        venue = offerers_factories.VenueFactory(
            name="L'encre et la plume",
            managingOfferer=user_offerer.offerer,
        )
        offerers_factories.VenuePricingPointLinkFactory(
            venue=venue,
            timespan=[now - datetime.timedelta(days=30), now - datetime.timedelta(days=7)],
        )
        venue_currently_used_for_pricing = offerers_factories.VenueFactory(
            publicName="Le Repos du Comptable",
            managingOfferer=user_offerer.offerer,
        )
        offerers_factories.VenuePricingPointLinkFactory(
            pricingPoint=venue_currently_used_for_pricing,
            venue=venue,
            timespan=[now - datetime.timedelta(days=7), None],
        )
        offerers_factories.VenueReimbursementPointLinkFactory(
            venue=venue,
            timespan=[now - datetime.timedelta(days=90), now - datetime.timedelta(days=14)],
        )
        venue_currently_used_for_reimbursement = offerers_factories.VenueFactory(
            name="Le nouveau lieu de remboursement",
            publicName="Le Palais de Midas",
            managingOfferer=user_offerer.offerer,
        )
        offerers_factories.VenueReimbursementPointLinkFactory(
            reimbursementPoint=venue_currently_used_for_reimbursement,
            venue=venue,
            timespan=[now - datetime.timedelta(days=14), None],
        )
        venue_id = venue.id
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
            "pricingPoint": {
                "id": venue_currently_used_for_pricing.id,
                "venueName": venue_currently_used_for_pricing.publicName,
                "siret": venue_currently_used_for_pricing.siret,
            },
            "reimbursementPointId": venue_currently_used_for_reimbursement.id,
            "dateCreated": format_into_utc_date(venue.dateCreated),
            "dateModifiedAtLastProvider": format_into_utc_date(venue.dateModifiedAtLastProvider),
            "demarchesSimplifieesApplicationId": venue.demarchesSimplifieesApplicationId,
            "departementCode": venue.departementCode,
            "description": venue.description,
            "dmsToken": venue.dmsToken,
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
            "bannerMeta": None,
            "nonHumanizedId": venue.id,
        }

        auth_request = client.with_session_auth(email=user_offerer.user.email)
        db.session.commit()  # clear SQLA cached objects
        n_queries = (
            testing.AUTHENTICATION_QUERIES  # 2
            + 1  # Venue and eager loading of relations
            + 1  # check_user_has_access_to_offerer()
        )
        with testing.assert_num_queries(n_queries):
            response = auth_request.get("/venues/%s" % humanize(venue_id))

        assert response.status_code == 200
        assert response.json == expected_serialized_venue

    def should_ignore_invalid_banner_metadata(self, client):
        user_offerer = offerers_factories.UserOffererFactory(user__email="user.pro@test.com")
        venue = offerers_factories.VenueFactory(
            name="L'encre et la plume",
            managingOfferer=user_offerer.offerer,
            bannerUrl="http://example.com/image_cropped.png",
            bannerMeta={
                "crop_params": {
                    "x_crop_percent": 0.29,
                    "y_crop_percent": 0.21,
                    "height_crop_percent": 0.42,
                    "width_crop_percent": 0.42,
                },
                "image_credit": "test",
                "random": "content",
                "should": "be_ignored",
            },
        )

        auth_request = client.with_session_auth(email=user_offerer.user.email)
        response = auth_request.get("/venues/%s" % humanize(venue.id))

        assert response.json["bannerMeta"] == {
            "crop_params": {
                "x_crop_percent": 0.29,
                "y_crop_percent": 0.21,
                "height_crop_percent": 0.42,
                "width_crop_percent": 0.42,
            },
            "image_credit": "test",
            "original_image_url": None,
        }

    def should_not_have_banner_metadata_when_venue_has_not_picture(self, client):
        user_offerer = offerers_factories.UserOffererFactory(user__email="user.pro@test.com")
        venue = offerers_factories.VenueFactory(
            name="L'encre et la plume",
            managingOfferer=user_offerer.offerer,
        )

        auth_request = client.with_session_auth(email=user_offerer.user.email)
        response = auth_request.get("/venues/%s" % humanize(venue.id))

        assert response.json["bannerMeta"] is None

    def should_set_default_crop_params_when_venue_picture_has_no_crop_params(self, client):
        user_offerer = offerers_factories.UserOffererFactory(user__email="user.pro@test.com")
        venue = offerers_factories.VenueFactory(
            name="L'encre et la plume",
            managingOfferer=user_offerer.offerer,
            bannerUrl="http://example.com/image_cropped.png",
            bannerMeta=None,
        )

        auth_request = client.with_session_auth(email=user_offerer.user.email)
        response = auth_request.get("/venues/%s" % humanize(venue.id))

        assert response.json["bannerMeta"]["crop_params"] == {
            "x_crop_percent": DO_NOT_CROP.x_crop_percent,
            "y_crop_percent": DO_NOT_CROP.y_crop_percent,
            "height_crop_percent": DO_NOT_CROP.height_crop_percent,
            "width_crop_percent": DO_NOT_CROP.width_crop_percent,
        }

    def should_not_override_metadata_when_venue_picture_has_no_crop_params(self, client):
        user_offerer = offerers_factories.UserOffererFactory(user__email="user.pro@test.com")
        venue = offerers_factories.VenueFactory(
            name="L'encre et la plume",
            managingOfferer=user_offerer.offerer,
            bannerUrl="http://example.com/image_cropped.png",
            bannerMeta={"image_credit": "test", "original_image_url": "http://example.com/original_image.png"},
        )

        auth_request = client.with_session_auth(email=user_offerer.user.email)
        response = auth_request.get("/venues/%s" % humanize(venue.id))

        assert response.json["bannerMeta"] == {
            "crop_params": {
                "x_crop_percent": DO_NOT_CROP.x_crop_percent,
                "y_crop_percent": DO_NOT_CROP.y_crop_percent,
                "height_crop_percent": DO_NOT_CROP.height_crop_percent,
                "width_crop_percent": DO_NOT_CROP.width_crop_percent,
            },
            "image_credit": "test",
            "original_image_url": "http://example.com/original_image.png",
        }

    def should_not_override_metadata_when_venue_picture_has_crop_params(self, client):
        user_offerer = offerers_factories.UserOffererFactory(user__email="user.pro@test.com")
        venue = offerers_factories.VenueFactory(
            name="L'encre et la plume",
            managingOfferer=user_offerer.offerer,
            bannerUrl="http://example.com/image_cropped.png",
            bannerMeta={
                "crop_params": {
                    "x_crop_percent": 0.29,
                    "y_crop_percent": 0.21,
                    "height_crop_percent": 0.42,
                    "width_crop_percent": 0.42,
                },
                "image_credit": "test 2",
            },
        )

        auth_request = client.with_session_auth(email=user_offerer.user.email)
        response = auth_request.get("/venues/%s" % humanize(venue.id))

        assert response.json["bannerMeta"] == {
            "crop_params": {
                "x_crop_percent": 0.29,
                "y_crop_percent": 0.21,
                "height_crop_percent": 0.42,
                "width_crop_percent": 0.42,
            },
            "image_credit": "test 2",
            "original_image_url": None,
        }

    def should_complete_crop_params_when_venue_picture_has_incomplete_crop_params(self, client):
        user_offerer = offerers_factories.UserOffererFactory(user__email="user.pro@test.com")
        venue = offerers_factories.VenueFactory(
            name="L'encre et la plume",
            managingOfferer=user_offerer.offerer,
            bannerUrl="http://example.com/image_cropped.png",
            bannerMeta={"crop_params": {"x_crop_percent": 0.29, "y_crop_percent": 0.21, "height_crop_percent": 0.42}},
        )

        auth_request = client.with_session_auth(email=user_offerer.user.email)
        response = auth_request.get("/venues/%s" % humanize(venue.id))

        assert response.json["bannerMeta"]["crop_params"] == {
            "x_crop_percent": 0.29,
            "y_crop_percent": 0.21,
            "height_crop_percent": 0.42,
            "width_crop_percent": DO_NOT_CROP.width_crop_percent,
        }

    def should_not_change_crop_params_when_venue_picture_has_complete_crop_params(self, client):
        user_offerer = offerers_factories.UserOffererFactory(user__email="user.pro@test.com")
        venue = offerers_factories.VenueFactory(
            name="L'encre et la plume",
            managingOfferer=user_offerer.offerer,
            bannerUrl="http://example.com/image_cropped.png",
            bannerMeta={
                "crop_params": {
                    "x_crop_percent": 0.29,
                    "y_crop_percent": 0.21,
                    "height_crop_percent": 0.42,
                    "width_crop_percent": 0.42,
                },
                "image_credit": "test",
            },
        )

        auth_request = client.with_session_auth(email=user_offerer.user.email)
        response = auth_request.get("/venues/%s" % humanize(venue.id))

        assert response.json["bannerMeta"]["crop_params"] == {
            "x_crop_percent": 0.29,
            "y_crop_percent": 0.21,
            "height_crop_percent": 0.42,
            "width_crop_percent": 0.42,
        }

    def should_complete_crop_params_when_venue_image_crop_params_is_null(self, client):
        user_offerer = offerers_factories.UserOffererFactory(user__email="user.pro@test.com")
        venue = offerers_factories.VenueFactory(
            name="L'encre et la plume",
            managingOfferer=user_offerer.offerer,
            bannerUrl="http://example.com/image_cropped.png",
            bannerMeta={"crop_params": None},
        )

        auth_request = client.with_session_auth(email=user_offerer.user.email)
        response = auth_request.get("/venues/%s" % humanize(venue.id))

        assert response.json["bannerMeta"] == {
            "crop_params": {
                "x_crop_percent": DO_NOT_CROP.x_crop_percent,
                "y_crop_percent": DO_NOT_CROP.y_crop_percent,
                "height_crop_percent": DO_NOT_CROP.height_crop_percent,
                "width_crop_percent": DO_NOT_CROP.width_crop_percent,
            },
            "image_credit": None,
            "original_image_url": None,
        }


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
