import datetime

import pytest

from pcapi.core import testing
from pcapi.core.educational import factories as educational_factories
import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.users.factories as users_factories
from pcapi.models import db
from pcapi.utils.date import format_into_utc_date
from pcapi.utils.image_conversion import DO_NOT_CROP


@pytest.mark.usefixtures("db_session")
class Returns200Test:
    def when_user_has_rights_on_managing_offerer(self, client, db_session):
        now = datetime.datetime.utcnow()
        user_offerer = offerers_factories.UserOffererFactory(user__email="user.pro@test.com")
        venue = offerers_factories.CollectiveVenueFactory(
            name="L'encre et la plume",
            managingOfferer=user_offerer.offerer,
            collectiveDescription="Description du lieu",
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
        dmsapplication = educational_factories.CollectiveDmsApplicationFactory(
            venue=venue,
        )
        expected_serialized_venue = {
            "address": venue.address,
            "audioDisabilityCompliant": venue.audioDisabilityCompliant,
            "bookingEmail": venue.bookingEmail,
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
            "dmsToken": "PRO-" + venue.dmsToken,
            "fieldsUpdated": venue.fieldsUpdated,
            "idAtProviders": venue.idAtProviders,
            "isPermanent": venue.isPermanent,
            "isVirtual": venue.isVirtual,
            "latitude": float(venue.latitude),
            "lastProviderId": venue.lastProviderId,
            "longitude": float(venue.longitude),
            "managingOfferer": {
                "address": venue.managingOfferer.address,
                "city": venue.managingOfferer.city,
                "dateCreated": format_into_utc_date(venue.managingOfferer.dateCreated),
                "demarchesSimplifieesApplicationId": venue.managingOfferer.demarchesSimplifieesApplicationId,
                "id": venue.managingOfferer.id,
                "isValidated": venue.managingOfferer.isValidated,
                "name": venue.managingOfferer.name,
                "postalCode": venue.managingOfferer.postalCode,
                "siren": venue.managingOfferer.siren,
            },
            "mentalDisabilityCompliant": venue.mentalDisabilityCompliant,
            "motorDisabilityCompliant": venue.motorDisabilityCompliant,
            "name": venue.name,
            "postalCode": venue.postalCode,
            "publicName": venue.publicName,
            "siret": venue.siret,
            "venueLabelId": venue.venueLabelId,
            "venueTypeCode": venue.venueTypeCode.name,
            "visualDisabilityCompliant": venue.visualDisabilityCompliant,
            "withdrawalDetails": None,
            "bannerUrl": venue.bannerUrl,
            "bannerMeta": {
                "crop_params": {
                    "height_crop_percent": 1.0,
                    "width_crop_percent": 1.0,
                    "x_crop_percent": 0.0,
                    "y_crop_percent": 0.0,
                },
                "image_credit": None,
                "original_image_url": None,
            },
            "id": venue.id,
            "collectiveAccessInformation": None,
            "collectiveDescription": "Description du lieu",
            "collectiveDomains": [],
            "collectiveEmail": None,
            "collectiveInterventionArea": ["75", "92"],
            "collectiveLegalStatus": None,
            "collectiveNetwork": None,
            "collectivePhone": None,
            "collectiveStudents": [],
            "collectiveWebsite": None,
            "collectiveSubCategoryId": None,
            "hasPendingBankInformationApplication": False,
            "collectiveDmsApplications": [
                {
                    "venueId": dmsapplication.venue.id,
                    "state": dmsapplication.state,
                    "procedure": dmsapplication.procedure,
                    "application": dmsapplication.application,
                    "lastChangeDate": format_into_utc_date(dmsapplication.lastChangeDate),
                    "depositDate": format_into_utc_date(dmsapplication.depositDate),
                    "expirationDate": format_into_utc_date(dmsapplication.expirationDate),
                    "buildDate": format_into_utc_date(dmsapplication.buildDate),
                    "instructionDate": None,
                    "processingDate": None,
                    "userDeletionDate": None,
                }
            ],
            "hasAdageId": True,
            "adageInscriptionDate": format_into_utc_date(venue.adageInscriptionDate),
        }
        db.session.expire_all()

        auth_request = client.with_session_auth(email=user_offerer.user.email)
        with testing.assert_no_duplicated_queries():
            response = auth_request.get("/venues/%s" % venue_id)

        assert response.status_code == 200
        assert response.json == expected_serialized_venue

    def when_user_has_rights_on_managing_offerer_with_no_adage_id(self, client):
        user_offerer = offerers_factories.UserOffererFactory(user__email="user.pro@test.com")
        venue = offerers_factories.CollectiveVenueFactory(
            name="L'encre et la plume",
            managingOfferer=user_offerer.offerer,
            collectiveDescription="Description du lieu",
            adageId=None,
            adageInscriptionDate=None,
        )
        venue_id = venue.id
        db.session.expire_all()

        auth_request = client.with_session_auth(email=user_offerer.user.email)
        with testing.assert_no_duplicated_queries():
            response = auth_request.get("/venues/%s" % venue_id)

        assert response.status_code == 200
        assert response.json["adageInscriptionDate"] is None
        assert response.json["hasAdageId"] is False

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
        response = auth_request.get("/venues/%s" % venue.id)

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
        response = auth_request.get("/venues/%s" % venue.id)

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
        response = auth_request.get("/venues/%s" % venue.id)

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
        response = auth_request.get("/venues/%s" % venue.id)

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
        response = auth_request.get("/venues/%s" % venue.id)

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
        response = auth_request.get("/venues/%s" % venue.id)

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
        response = auth_request.get("/venues/%s" % venue.id)

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
        response = auth_request.get("/venues/%s" % venue.id)

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
    def when_current_user_doesnt_have_rights(self, client):
        # given
        pro = users_factories.ProFactory(email="user.pro@example.com")
        venue = offerers_factories.VenueFactory(name="L'encre et la plume")

        # when
        auth_request = client.with_session_auth(email=pro.email)
        response = auth_request.get("/venues/%s" % venue.id)

        # then
        assert response.status_code == 403
        assert response.json["global"] == [
            "Vous n'avez pas les droits d'accès suffisant pour accéder à cette information."
        ]
