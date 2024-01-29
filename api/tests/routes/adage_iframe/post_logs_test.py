import logging

from flask import url_for
import pytest

from pcapi.core.educational import utils
from pcapi.routes.adage_iframe.serialization.adage_authentication import AdageFrontRoles

from tests.routes.adage_iframe.utils_create_test_token import create_adage_valid_token_with_email


EMAIL = "test@mail.com"
UAI = "EAU123"


@pytest.fixture(name="test_client")
def test_client_fixture(client):
    return client.with_adage_token(email=EMAIL, uai=UAI)


class LogsTest:
    def test_log_catalog_view(self, client, caplog):
        # given
        adage_jwt_fake_valid_token = create_adage_valid_token_with_email(email="test@mail.com")
        client.auth_header = {"Authorization": f"Bearer {adage_jwt_fake_valid_token}"}

        # when
        with caplog.at_level(logging.INFO):
            response = client.post(
                "/adage-iframe/logs/catalog-view",
                json={"source": "partnersMap", "iframeFrom": "for_my_institution", "queryId": "1234a"},
            )

        # then
        assert response.status_code == 204
        assert caplog.records[0].message == "CatalogView"
        assert caplog.records[0].extra == {
            "analyticsSource": "adage",
            "source": "partnersMap",
            "queryId": "1234a",
            "from": "for_my_institution",
            "uai": "EAU123",
            "user_role": AdageFrontRoles.READONLY,
            "userId": "f0e2a21bcf499cbc713c47d8f034d66e90a99f9ffcfe96466c9971dfdc5c9816",
        }

    @pytest.mark.parametrize(
        "playlist_type,element_id,index,offer_id,venue_id,domain_id",
        [
            ("offer", 34, 1, 34, None, None),
            ("venue", 45, 2, None, 45, None),
            ("domain", 56, None, None, None, 56),
        ],
    )
    def test_log_consult_playlist_element(
        self, client, caplog, playlist_type, element_id, index, offer_id, venue_id, domain_id
    ):
        # given
        adage_jwt_fake_valid_token = create_adage_valid_token_with_email(email="test@mail.com")
        client.auth_header = {"Authorization": f"Bearer {adage_jwt_fake_valid_token}"}

        # when
        with caplog.at_level(logging.INFO):
            response = client.post(
                "/adage-iframe/logs/consult-playlist-element",
                json={
                    "source": "partnersMap",
                    "iframeFrom": "for_my_institution",
                    "queryId": "1234a",
                    "elementId": element_id,
                    "index": index,
                    "playlistId": 99,
                    "playlistType": playlist_type,
                },
            )

        # then
        assert response.status_code == 204
        assert caplog.records[0].message == "ConsultPlaylistElement"
        assert caplog.records[0].extra == {
            "analyticsSource": "adage",
            "queryId": "1234a",
            "from": "for_my_institution",
            "uai": "EAU123",
            "user_role": AdageFrontRoles.READONLY,
            "userId": "f0e2a21bcf499cbc713c47d8f034d66e90a99f9ffcfe96466c9971dfdc5c9816",
            "playlistId": 99,
            "offerId": offer_id,
            "venueId": venue_id,
            "domainId": domain_id,
            "index": index,
        }

    def test_log_has_seen_whole_playlist(self, client, caplog):
        # given
        adage_jwt_fake_valid_token = create_adage_valid_token_with_email(email="test@mail.com")
        client.auth_header = {"Authorization": f"Bearer {adage_jwt_fake_valid_token}"}

        # when
        with caplog.at_level(logging.INFO):
            response = client.post(
                "/adage-iframe/logs/has-seen-whole-playlist",
                json={
                    "source": "partnersMap",
                    "iframeFrom": "for_my_institution",
                    "queryId": "1234a",
                    "playlistId": 99,
                    "playlistType": "offer",
                },
            )

        # then
        assert response.status_code == 204
        assert caplog.records[0].message == "HasSeenWholePlaylist"
        assert caplog.records[0].extra == {
            "analyticsSource": "adage",
            "queryId": "1234a",
            "from": "for_my_institution",
            "uai": "EAU123",
            "user_role": AdageFrontRoles.READONLY,
            "userId": "f0e2a21bcf499cbc713c47d8f034d66e90a99f9ffcfe96466c9971dfdc5c9816",
            "playlistId": 99,
        }

    def test_log_search_button(self, client, caplog):
        # given
        adage_jwt_fake_valid_token = create_adage_valid_token_with_email(email="test@mail.com")
        client.auth_header = {"Authorization": f"Bearer {adage_jwt_fake_valid_token}"}

        # when
        with caplog.at_level(logging.INFO):
            response = client.post(
                "/adage-iframe/logs/search-button",
                json={
                    "filters": [
                        "departments",
                        "institutionId",
                    ],
                    "iframeFrom": "for_my_institution",
                    "resultsCount": 0,
                    "isFromNoResult": "true",
                },
            )

        # then
        assert response.status_code == 204
        assert caplog.records[0].message == "SearchButtonClicked"
        assert caplog.records[0].extra == {
            "analyticsSource": "adage",
            "from": "for_my_institution",
            "filters": ["departments", "institutionId"],
            "queryId": None,
            "resultsCount": 0,
            "userId": "f0e2a21bcf499cbc713c47d8f034d66e90a99f9ffcfe96466c9971dfdc5c9816",
            "uai": "EAU123",
            "user_role": AdageFrontRoles.READONLY,
            "isFromNoResult": True,
        }

    def test_log_offer_detail(self, client, caplog):
        # given
        adage_jwt_fake_valid_token = create_adage_valid_token_with_email(email="test@mail.com")
        client.auth_header = {"Authorization": f"Bearer {adage_jwt_fake_valid_token}"}

        # when
        with caplog.at_level(logging.INFO):
            response = client.post(
                "/adage-iframe/logs/offer-detail",
                json={
                    "stockId": 1,
                    "iframeFrom": "for_my_institution",
                    "queryId": "1234a",
                },
            )

        # then
        assert response.status_code == 204
        assert caplog.records[0].message == "OfferDetailButtonClick"
        assert caplog.records[0].extra == {
            "analyticsSource": "adage",
            "stockId": 1,
            "queryId": "1234a",
            "from": "for_my_institution",
            "userId": "f0e2a21bcf499cbc713c47d8f034d66e90a99f9ffcfe96466c9971dfdc5c9816",
            "uai": "EAU123",
            "user_role": AdageFrontRoles.READONLY,
        }

    def test_log_offer_template_details_button_click(self, client, caplog):
        # given
        adage_jwt_fake_valid_token = create_adage_valid_token_with_email(email="test@mail.com")
        client.auth_header = {"Authorization": f"Bearer {adage_jwt_fake_valid_token}"}

        # when
        with caplog.at_level(logging.INFO):
            response = client.post(
                "/adage-iframe/logs/offer-template-detail",
                json={"offerId": 1, "iframeFrom": "for_my_institution"},
            )

        # then
        assert response.status_code == 204
        assert caplog.records[0].message == "TemplateOfferDetailButtonClick"
        assert caplog.records[0].extra == {
            "analyticsSource": "adage",
            "offerId": 1,
            "queryId": None,
            "from": "for_my_institution",
            "userId": "f0e2a21bcf499cbc713c47d8f034d66e90a99f9ffcfe96466c9971dfdc5c9816",
            "uai": "EAU123",
            "user_role": AdageFrontRoles.READONLY,
        }

    def test_log_booking_modal_button_click(self, client, caplog):
        # given
        adage_jwt_fake_valid_token = create_adage_valid_token_with_email(email="test@mail.com")
        client.auth_header = {"Authorization": f"Bearer {adage_jwt_fake_valid_token}"}

        # when
        with caplog.at_level(logging.INFO):
            response = client.post(
                "/adage-iframe/logs/booking-modal-button",
                json={"stockId": 1, "iframeFrom": "for_my_institution", "queryId": "1234a"},
            )

        # then
        assert response.status_code == 204
        assert caplog.records[0].message == "BookingModalButtonClick"
        assert caplog.records[0].extra == {
            "analyticsSource": "adage",
            "stockId": 1,
            "queryId": "1234a",
            "from": "for_my_institution",
            "userId": "f0e2a21bcf499cbc713c47d8f034d66e90a99f9ffcfe96466c9971dfdc5c9816",
            "uai": "EAU123",
            "user_role": AdageFrontRoles.READONLY,
            "isFromNoResult": None,
        }

    def test_log_contact_modal_button_click(self, client, caplog):
        # given
        adage_jwt_fake_valid_token = create_adage_valid_token_with_email(email="test@mail.com")
        client.auth_header = {"Authorization": f"Bearer {adage_jwt_fake_valid_token}"}

        # when
        with caplog.at_level(logging.INFO):
            response = client.post(
                "/adage-iframe/logs/offer-template-detail",
                json={
                    "offerId": 1,
                    "iframeFrom": "for_my_institution",
                    "queryId": None,
                },
            )

        # then
        assert response.status_code == 204
        assert caplog.records[0].message == "TemplateOfferDetailButtonClick"
        assert caplog.records[0].extra == {
            "analyticsSource": "adage",
            "offerId": 1,
            "queryId": None,
            "from": "for_my_institution",
            "userId": "f0e2a21bcf499cbc713c47d8f034d66e90a99f9ffcfe96466c9971dfdc5c9816",
            "uai": "EAU123",
            "user_role": AdageFrontRoles.READONLY,
        }

    def test_log_fav_offer_button_click(self, client, caplog):
        # given
        adage_jwt_fake_valid_token = create_adage_valid_token_with_email(email="test@mail.com")
        client.auth_header = {"Authorization": f"Bearer {adage_jwt_fake_valid_token}"}

        # when
        with caplog.at_level(logging.INFO):
            response = client.post(
                "/adage-iframe/logs/fav-offer",
                json={"offerId": 1, "iframeFrom": "for_my_institution", "isFavorite": True},
            )

        # then
        assert response.status_code == 204
        assert caplog.records[0].message == "FavOfferButtonClick"
        assert caplog.records[0].extra == {
            "analyticsSource": "adage",
            "offerId": 1,
            "queryId": None,
            "isFavorite": True,
            "from": "for_my_institution",
            "userId": "f0e2a21bcf499cbc713c47d8f034d66e90a99f9ffcfe96466c9971dfdc5c9816",
            "uai": "EAU123",
            "user_role": AdageFrontRoles.READONLY,
            "isFromNoResult": None,
        }

    def test_log_header_link_click(self, client, caplog):
        # given
        test_client = client.with_adage_token(email="test@mail.com", uai="123456")

        # when
        with caplog.at_level(logging.INFO):
            response = test_client.post(
                "/adage-iframe/logs/header-link-click",
                json={"header_link_name": "search", "iframeFrom": "for_my_institution"},
            )

        # then
        assert response.status_code == 204
        record = next(record for record in caplog.records if record.message == "HeaderLinkClick")
        assert record is not None
        assert record.extra == {
            "analyticsSource": "adage",
            "header_link_name": "search",
            "from": "for_my_institution",
            "queryId": None,
            "userId": "f0e2a21bcf499cbc713c47d8f034d66e90a99f9ffcfe96466c9971dfdc5c9816",
            "uai": "123456",
            "user_role": AdageFrontRoles.READONLY,
        }

    def test_log_request_form_popin_dismiss(self, client, caplog):
        # given
        test_client = client.with_adage_token(email="test@mail.com", uai="EAU123")

        # when
        with caplog.at_level(logging.INFO):
            response = test_client.post(
                "/adage-iframe/logs/request-popin-dismiss",
                json={
                    "collectiveOfferTemplateId": 1,
                    "phoneNumber": "0601020304",
                    "requestedDate": "2022-12-02",
                    "totalStudents": 30,
                    "totalTeachers": 2,
                    "comment": "La première règle du Fight Club est: il est interdit de parler du Fight Club",
                    "iframeFrom": "for_my_institution",
                },
            )

        # then
        assert response.status_code == 204
        record = [record for record in caplog.records if record.message == "RequestPopinDismiss"][0]
        assert record.extra == {
            "analyticsSource": "adage",
            "from": "for_my_institution",
            "collectiveOfferTemplateId": 1,
            "phoneNumber": "0601020304",
            "requestedDate": "2022-12-02",
            "totalStudents": 30,
            "totalTeachers": 2,
            "comment": "La première règle du Fight Club est: il est interdit de parler du Fight Club",
            "userId": "f0e2a21bcf499cbc713c47d8f034d66e90a99f9ffcfe96466c9971dfdc5c9816",
            "uai": "EAU123",
            "user_role": AdageFrontRoles.READONLY,
            "queryId": None,
            "isFromNoResult": None,
        }

    def test_log_tracking_filter(self, client, caplog):
        # given
        test_client = client.with_adage_token(email="test@mail.com", uai="EAU123")

        # when
        with caplog.at_level(logging.INFO):
            response = test_client.post(
                "/adage-iframe/logs/tracking-filter",
                json={
                    "queryId": "1",
                    "resultNumber": 36,
                    "filterValues": {
                        "key1": "value1",
                        "key2": "value2",
                    },
                    "iframeFrom": "for_my_institution",
                },
            )

        # then
        assert response.status_code == 204
        record = [record for record in caplog.records if record.message == "TrackingFilter"][0]
        assert record.extra == {
            "analyticsSource": "adage",
            "from": "for_my_institution",
            "userId": "f0e2a21bcf499cbc713c47d8f034d66e90a99f9ffcfe96466c9971dfdc5c9816",
            "uai": "EAU123",
            "user_role": AdageFrontRoles.READONLY,
            "queryId": "1",
            "resultNumber": 36,
            "filterValues": {
                "key1": "value1",
                "key2": "value2",
            },
            "isFromNoResult": None,
        }

    def test_log_closer_sastifaction_survey(self, client, caplog):
        # given
        adage_jwt_fake_valid_token = create_adage_valid_token_with_email(email="test@mail.com")
        client.auth_header = {"Authorization": f"Bearer {adage_jwt_fake_valid_token}"}

        # when
        with caplog.at_level(logging.INFO):
            response = client.post(
                "/adage-iframe/logs/sat-survey",
                json={"iframeFrom": "for_my_institution", "queryId": "1234a"},
            )

        # then
        assert response.status_code == 204
        assert caplog.records[0].message == "OpenSatisfactionSurvey"
        assert caplog.records[0].extra == {
            "analyticsSource": "adage",
            "queryId": "1234a",
            "from": "for_my_institution",
            "uai": "EAU123",
            "user_role": AdageFrontRoles.READONLY,
            "userId": "f0e2a21bcf499cbc713c47d8f034d66e90a99f9ffcfe96466c9971dfdc5c9816",
        }

    def test_log_tracking_autocompletion(self, client, caplog):
        # given
        adage_jwt_fake_valid_token = create_adage_valid_token_with_email(email="test@mail.com")
        client.auth_header = {"Authorization": f"Bearer {adage_jwt_fake_valid_token}"}

        # when
        with caplog.at_level(logging.INFO):
            response = client.post(
                "/adage-iframe/logs/tracking-autocompletion",
                json={
                    "suggestionType": "offer category",
                    "suggestionValue": "ai confiance, crois en moi, que je puisse, veiller sur toi",
                    "iframeFrom": "for_my_institution",
                    "queryId": "1234a",
                },
            )

        # then
        assert response.status_code == 204
        assert caplog.records[0].message == "logAutocompleteSuggestionClicked"
        record = [record for record in caplog.records if record.message == "logAutocompleteSuggestionClicked"][0]
        assert record.extra == {
            "analyticsSource": "adage",
            "from": "for_my_institution",
            "queryId": "1234a",
            "suggestionType": "offer category",
            "suggestionValue": "ai confiance, crois en moi, que je puisse, veiller sur toi",
            "userId": "f0e2a21bcf499cbc713c47d8f034d66e90a99f9ffcfe96466c9971dfdc5c9816",
            "uai": "EAU123",
            "user_role": AdageFrontRoles.READONLY,
        }

    def test_log_adage_map(self, client, caplog):
        # given
        adage_jwt_fake_valid_token = create_adage_valid_token_with_email(email="test@mail.com")
        client.auth_header = {"Authorization": f"Bearer {adage_jwt_fake_valid_token}"}

        # when
        with caplog.at_level(logging.INFO):
            response = client.post(
                "/adage-iframe/logs/tracking-map",
                json={"iframeFrom": "for_my_institution", "queryId": "1234a"},
            )

        # then
        assert response.status_code == 204
        assert caplog.records[0].message == "adageMapClicked"
        assert caplog.records[0].extra == {
            "analyticsSource": "adage",
            "queryId": "1234a",
            "from": "for_my_institution",
            "uai": "EAU123",
            "user_role": AdageFrontRoles.READONLY,
            "userId": "f0e2a21bcf499cbc713c47d8f034d66e90a99f9ffcfe96466c9971dfdc5c9816",
            "isFromNoResult": None,
        }

    def test_log_has_seen_all_playlist(self, client, caplog):
        # given
        adage_jwt_fake_valid_token = create_adage_valid_token_with_email(email="test@mail.com")
        client.auth_header = {"Authorization": f"Bearer {adage_jwt_fake_valid_token}"}

        # when
        with caplog.at_level(logging.INFO):
            response = client.post(
                "/adage-iframe/logs/playlist",
                json={"iframeFrom": "for_my_institution", "queryId": "1234a"},
            )

        # then
        assert response.status_code == 204
        assert caplog.records[0].message == "HasSeenAllPlaylist"
        assert caplog.records[0].extra == {
            "analyticsSource": "adage",
            "queryId": "1234a",
            "from": "for_my_institution",
            "uai": "EAU123",
            "user_role": AdageFrontRoles.READONLY,
            "userId": "f0e2a21bcf499cbc713c47d8f034d66e90a99f9ffcfe96466c9971dfdc5c9816",
        }

    def test_log_search_show_more(self, client, caplog):
        # given
        adage_jwt_fake_valid_token = create_adage_valid_token_with_email(email="test@mail.com")
        client.auth_header = {"Authorization": f"Bearer {adage_jwt_fake_valid_token}"}

        # when
        with caplog.at_level(logging.INFO):
            response = client.post(
                "/adage-iframe/logs/search-show-more",
                json={
                    "iframeFrom": "for_my_institution",
                    "queryId": "1234a",
                    "source": "partnersMap",
                },
            )

        # then
        assert response.status_code == 204
        assert caplog.records[0].message == "SearchShowMore"
        assert caplog.records[0].extra == {
            "analyticsSource": "adage",
            "source": "partnersMap",
            "queryId": "1234a",
            "from": "for_my_institution",
            "uai": "EAU123",
            "user_role": AdageFrontRoles.READONLY,
            "userId": "f0e2a21bcf499cbc713c47d8f034d66e90a99f9ffcfe96466c9971dfdc5c9816",
        }

    def test_log_tracking_cta_share(self, test_client, caplog):
        dst = url_for("adage_iframe.log_tracking_cta_share")

        data = {
            "source": "source",
            "offerId": 1,
            "iframeFrom": "some_iframe",
        }

        with caplog.at_level(logging.INFO):
            response = test_client.post(dst, json=data)

        assert response.status_code == 204

        try:
            record = next(record for record in caplog.records if record.message == "TrackingCTAShare")
        except StopIteration:
            pytest.fail("Should be a record with the expected message")

        assert record.extra == {
            "source": data["source"],
            "offerId": data["offerId"],
            "from": data["iframeFrom"],
            "queryId": None,
            "isFromNoResult": None,
            "user_role": AdageFrontRoles.READONLY,
            "uai": UAI,
            "userId": utils.get_hashed_user_id(EMAIL),
            "analyticsSource": "adage",
        }
