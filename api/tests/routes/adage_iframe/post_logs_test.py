import logging

import pytest
from flask import url_for

from pcapi.core.educational import utils
from pcapi.core.educational.models import AdageFrontRoles
from pcapi.core.educational.utils import get_hashed_user_id
from pcapi.routes.adage_iframe.serialization.logs import PaginationType


EMAIL = "test@mail.com"
UAI = "EAU123"


@pytest.fixture(name="test_client")
def test_client_fixture(client):
    return client.with_adage_token(email=EMAIL, uai=UAI)


class LogsTest:
    def test_log_catalog_view(self, test_client, caplog):
        with caplog.at_level(logging.INFO):
            response = test_client.post(
                url_for("adage_iframe.log_catalog_view"),
                json={"source": "partnersMap", "iframeFrom": "for_my_institution", "queryId": "1234a"},
            )

        assert response.status_code == 204
        assert caplog.records[0].message == "CatalogView"
        assert caplog.records[0].extra == {
            "analyticsSource": "adage",
            "source": "partnersMap",
            "queryId": "1234a",
            "from": "for_my_institution",
            "uai": UAI,
            "user_role": AdageFrontRoles.READONLY,
            "userId": get_hashed_user_id(EMAIL),
        }

    def test_log_offer_list_view_switch(self, test_client, caplog):
        with caplog.at_level(logging.INFO):
            response = test_client.post(
                url_for("adage_iframe.log_offer_list_view_switch"),
                json={"source": "offer_switch", "iframeFrom": "playlist", "queryId": "1234", "isMobile": True},
            )

        assert response.status_code == 204
        assert caplog.records[0].message == "OfferListSwitch"
        assert caplog.records[0].extra == {
            "analyticsSource": "adage",
            "source": "offer_switch",
            "queryId": "1234",
            "isMobile": True,
            "from": "playlist",
            "uai": UAI,
            "user_role": AdageFrontRoles.READONLY,
            "userId": get_hashed_user_id(EMAIL),
        }

    @pytest.mark.parametrize(
        "playlist_type,index,offer_id,venue_id,domain_id",
        [
            ("offer", 1, 34, None, None),
            ("venue", 2, None, 45, None),
            ("domain", 3, None, None, 56),
        ],
    )
    def test_log_consult_playlist_element(
        self, test_client, caplog, playlist_type, index, offer_id, venue_id, domain_id
    ):
        with caplog.at_level(logging.INFO):
            response = test_client.post(
                url_for("adage_iframe.log_consult_playlist_element"),
                json={
                    "source": "partnersMap",
                    "iframeFrom": "for_my_institution",
                    "queryId": "1234a",
                    "index": index,
                    "playlistId": 99,
                    "playlistType": playlist_type,
                    "offerId": offer_id,
                    "venueId": venue_id,
                    "domainId": domain_id,
                },
            )

        assert response.status_code == 204
        assert caplog.records[0].message == "ConsultPlaylistElement"
        assert caplog.records[0].extra == {
            "analyticsSource": "adage",
            "queryId": "1234a",
            "from": "for_my_institution",
            "uai": UAI,
            "user_role": AdageFrontRoles.READONLY,
            "userId": get_hashed_user_id(EMAIL),
            "playlistId": 99,
            "offerId": offer_id,
            "venueId": venue_id,
            "domainId": domain_id,
            "index": index,
        }

    def test_log_has_seen_whole_playlist(self, test_client, caplog):
        with caplog.at_level(logging.INFO):
            response = test_client.post(
                url_for("adage_iframe.log_has_seen_whole_playlist"),
                json={
                    "source": "partnersMap",
                    "iframeFrom": "for_my_institution",
                    "queryId": "1234a",
                    "playlistId": 99,
                    "playlistType": "offer",
                },
            )

        assert response.status_code == 204
        assert caplog.records[0].message == "HasSeenWholePlaylist"
        assert caplog.records[0].extra == {
            "analyticsSource": "adage",
            "queryId": "1234a",
            "from": "for_my_institution",
            "uai": UAI,
            "user_role": AdageFrontRoles.READONLY,
            "userId": get_hashed_user_id(EMAIL),
            "playlistId": 99,
        }

    def test_log_search_button(self, test_client, caplog):
        with caplog.at_level(logging.INFO):
            response = test_client.post(
                url_for("adage_iframe.log_search_button_click"),
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

        assert response.status_code == 204
        assert caplog.records[0].message == "SearchButtonClicked"
        assert caplog.records[0].extra == {
            "analyticsSource": "adage",
            "from": "for_my_institution",
            "filters": ["departments", "institutionId"],
            "queryId": None,
            "resultsCount": 0,
            "userId": get_hashed_user_id(EMAIL),
            "uai": UAI,
            "user_role": AdageFrontRoles.READONLY,
            "isFromNoResult": True,
        }

    def test_log_offer_detail(self, test_client, caplog):
        with caplog.at_level(logging.INFO):
            response = test_client.post(
                url_for("adage_iframe.log_offer_details_button_click"),
                json={
                    "stockId": 1,
                    "iframeFrom": "for_my_institution",
                    "queryId": "1234a",
                    "vueType": "vt",
                },
            )

        assert response.status_code == 204
        assert caplog.records[0].message == "OfferDetailButtonClick"
        assert caplog.records[0].extra == {
            "analyticsSource": "adage",
            "stockId": 1,
            "queryId": "1234a",
            "from": "for_my_institution",
            "userId": get_hashed_user_id(EMAIL),
            "uai": UAI,
            "user_role": AdageFrontRoles.READONLY,
            "vueType": "vt",
        }

    def test_log_offer_template_details_button_click(self, test_client, caplog):
        with caplog.at_level(logging.INFO):
            response = test_client.post(
                url_for("adage_iframe.log_offer_template_details_button_click"),
                json={"offerId": 1, "iframeFrom": "for_my_institution", "vueType": "vt"},
            )

        assert response.status_code == 204
        assert caplog.records[0].message == "TemplateOfferDetailButtonClick"
        assert caplog.records[0].extra == {
            "analyticsSource": "adage",
            "offerId": 1,
            "queryId": None,
            "from": "for_my_institution",
            "userId": get_hashed_user_id(EMAIL),
            "uai": UAI,
            "user_role": AdageFrontRoles.READONLY,
            "vueType": "vt",
        }

    def test_log_booking_modal_button_click(self, test_client, caplog):
        with caplog.at_level(logging.INFO):
            response = test_client.post(
                url_for("adage_iframe.log_booking_modal_button_click"),
                json={"stockId": 1, "iframeFrom": "for_my_institution", "queryId": "1234a"},
            )

        assert response.status_code == 204
        assert caplog.records[0].message == "BookingModalButtonClick"
        assert caplog.records[0].extra == {
            "analyticsSource": "adage",
            "stockId": 1,
            "queryId": "1234a",
            "from": "for_my_institution",
            "userId": get_hashed_user_id(EMAIL),
            "uai": UAI,
            "user_role": AdageFrontRoles.READONLY,
            "isFromNoResult": None,
        }

    def test_log_contact_modal_button_click(self, test_client, caplog):
        with caplog.at_level(logging.INFO):
            response = test_client.post(
                url_for("adage_iframe.log_contact_modal_button_click"),
                json={
                    "offerId": 1,
                    "iframeFrom": "contact_modal",
                    "playlistId": 0,
                },
            )

        assert response.status_code == 204
        assert caplog.records[0].message == "ContactModalButtonClick"
        assert caplog.records[0].extra == {
            "analyticsSource": "adage",
            "offerId": 1,
            "playlistId": 0,
            "queryId": None,
            "from": "contact_modal",
            "userId": get_hashed_user_id(EMAIL),
            "uai": UAI,
            "user_role": AdageFrontRoles.READONLY,
            "isFromNoResult": None,
        }

    def test_log_fav_offer_button_click(self, test_client, caplog):
        with caplog.at_level(logging.INFO):
            response = test_client.post(
                url_for("adage_iframe.log_fav_offer_button_click"),
                json={
                    "offerId": 1,
                    "iframeFrom": "for_my_institution",
                    "isFavorite": True,
                    "vueType": "vt",
                    "playlistId": 0,
                },
            )

        assert response.status_code == 204
        assert caplog.records[0].message == "FavOfferButtonClick"
        assert caplog.records[0].extra == {
            "analyticsSource": "adage",
            "offerId": 1,
            "playlistId": 0,
            "queryId": None,
            "isFavorite": True,
            "from": "for_my_institution",
            "userId": get_hashed_user_id(EMAIL),
            "uai": UAI,
            "user_role": AdageFrontRoles.READONLY,
            "isFromNoResult": None,
            "vueType": "vt",
        }

    def test_log_header_link_click(self, test_client, caplog):
        with caplog.at_level(logging.INFO):
            response = test_client.post(
                url_for("adage_iframe.log_header_link_click"),
                json={"header_link_name": "search", "iframeFrom": "for_my_institution"},
            )

        assert response.status_code == 204
        record = next(record for record in caplog.records if record.message == "HeaderLinkClick")
        assert record is not None
        assert record.extra == {
            "analyticsSource": "adage",
            "header_link_name": "search",
            "from": "for_my_institution",
            "queryId": None,
            "userId": get_hashed_user_id(EMAIL),
            "uai": UAI,
            "user_role": AdageFrontRoles.READONLY,
        }

    def test_log_request_form_popin_dismiss(self, test_client, caplog):
        with caplog.at_level(logging.INFO):
            response = test_client.post(
                url_for("adage_iframe.log_request_form_popin_dismiss"),
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
            "userId": get_hashed_user_id(EMAIL),
            "uai": UAI,
            "user_role": AdageFrontRoles.READONLY,
            "queryId": None,
            "isFromNoResult": None,
        }

    def test_log_tracking_filter(self, test_client, caplog):
        with caplog.at_level(logging.INFO):
            response = test_client.post(
                url_for("adage_iframe.log_tracking_filter"),
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

        assert response.status_code == 204
        record = [record for record in caplog.records if record.message == "TrackingFilter"][0]
        assert record.extra == {
            "analyticsSource": "adage",
            "from": "for_my_institution",
            "userId": get_hashed_user_id(EMAIL),
            "uai": UAI,
            "user_role": AdageFrontRoles.READONLY,
            "queryId": "1",
            "resultNumber": 36,
            "filterValues": {
                "key1": "value1",
                "key2": "value2",
            },
            "isFromNoResult": None,
        }

    def test_log_tracking_filter_spam(self, test_client, caplog):
        url = url_for("adage_iframe.log_tracking_filter")
        data = {
            "queryId": "1",
            "resultNumber": 36,
            "filterValues": {"key1": "value1", "key2": "value2"},
            "iframeFrom": "for_my_institution",
        }

        with caplog.at_level(logging.INFO):
            for _ in range(3):
                response = test_client.post(url, json=data)
                assert response.status_code == 204

        tracking_records = [record for record in caplog.records if record.message == "TrackingFilter"]
        assert len(tracking_records) == 1

    def test_log_closer_sastifaction_survey(self, test_client, caplog):
        with caplog.at_level(logging.INFO):
            response = test_client.post(
                url_for("adage_iframe.log_open_satisfaction_survey"),
                json={"iframeFrom": "for_my_institution", "queryId": "1234a"},
            )

        assert response.status_code == 204
        assert caplog.records[0].message == "OpenSatisfactionSurvey"
        assert caplog.records[0].extra == {
            "analyticsSource": "adage",
            "queryId": "1234a",
            "from": "for_my_institution",
            "uai": UAI,
            "user_role": AdageFrontRoles.READONLY,
            "userId": get_hashed_user_id(EMAIL),
        }

    def test_log_tracking_autocompletion(self, test_client, caplog):
        with caplog.at_level(logging.INFO):
            response = test_client.post(
                url_for("adage_iframe.log_tracking_autocomplete_suggestion_click"),
                json={
                    "suggestionType": "offer category",
                    "suggestionValue": "ai confiance, crois en moi, que je puisse, veiller sur toi",
                    "iframeFrom": "for_my_institution",
                    "queryId": "1234a",
                },
            )

        assert response.status_code == 204
        assert caplog.records[0].message == "logAutocompleteSuggestionClicked"
        record = [record for record in caplog.records if record.message == "logAutocompleteSuggestionClicked"][0]
        assert record.extra == {
            "analyticsSource": "adage",
            "from": "for_my_institution",
            "queryId": "1234a",
            "suggestionType": "offer category",
            "suggestionValue": "ai confiance, crois en moi, que je puisse, veiller sur toi",
            "userId": get_hashed_user_id(EMAIL),
            "uai": UAI,
            "user_role": AdageFrontRoles.READONLY,
        }

    def test_log_adage_map(self, test_client, caplog):
        with caplog.at_level(logging.INFO):
            response = test_client.post(
                url_for("adage_iframe.log_tracking_map"),
                json={"iframeFrom": "for_my_institution", "queryId": "1234a"},
            )

        assert response.status_code == 204
        assert caplog.records[0].message == "adageMapClicked"
        assert caplog.records[0].extra == {
            "analyticsSource": "adage",
            "queryId": "1234a",
            "from": "for_my_institution",
            "uai": UAI,
            "user_role": AdageFrontRoles.READONLY,
            "userId": get_hashed_user_id(EMAIL),
            "isFromNoResult": None,
        }

    def test_log_has_seen_all_playlist(self, test_client, caplog):
        with caplog.at_level(logging.INFO):
            response = test_client.post(
                url_for("adage_iframe.log_has_seen_all_playlist"),
                json={"iframeFrom": "for_my_institution", "queryId": "1234a"},
            )

        assert response.status_code == 204
        assert caplog.records[0].message == "HasSeenAllPlaylist"
        assert caplog.records[0].extra == {
            "analyticsSource": "adage",
            "queryId": "1234a",
            "from": "for_my_institution",
            "uai": UAI,
            "user_role": AdageFrontRoles.READONLY,
            "userId": get_hashed_user_id(EMAIL),
        }

    def test_log_search_show_more(self, test_client, caplog):
        with caplog.at_level(logging.INFO):
            response = test_client.post(
                url_for("adage_iframe.log_search_show_more"),
                json={"iframeFrom": "for_my_institution", "queryId": "1234a", "source": "partnersMap", "type": "next"},
            )

        assert response.status_code == 204
        assert caplog.records[0].message == "SearchShowMore"
        assert caplog.records[0].extra == {
            "analyticsSource": "adage",
            "source": "partnersMap",
            "queryId": "1234a",
            "type": PaginationType.NEXT,
            "from": "for_my_institution",
            "uai": UAI,
            "user_role": AdageFrontRoles.READONLY,
            "userId": get_hashed_user_id(EMAIL),
        }

    def test_log_tracking_cta_share(self, test_client, caplog):
        dst = url_for("adage_iframe.log_tracking_cta_share")

        data = {
            "source": "source",
            "offerId": 1,
            "iframeFrom": "some_iframe",
            "vueType": "vt",
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
            "vueType": "vt",
        }

    def test_log_contact_url_button_click(self, test_client, caplog):
        with caplog.at_level(logging.INFO):
            response = test_client.post(
                url_for("adage_iframe.log_contact_url_click"),
                json={
                    "offerId": 1,
                    "iframeFrom": "contact_modal",
                },
            )

        assert response.status_code == 204
        assert caplog.records[0].message == "ContactUrlClick"
        assert caplog.records[0].extra == {
            "analyticsSource": "adage",
            "offerId": 1,
            "queryId": None,
            "from": "contact_modal",
            "userId": get_hashed_user_id(EMAIL),
            "uai": UAI,
            "user_role": AdageFrontRoles.READONLY,
            "isFromNoResult": None,
        }

    def test_log_open_highlight_banner(self, test_client, caplog):
        with caplog.at_level(logging.INFO):
            response = test_client.post(
                url_for("adage_iframe.log_open_highlight_banner"),
                json={"iframeFrom": "search", "banner": "TFMAC-2025", "queryId": "1234a"},
            )

        assert response.status_code == 204
        assert caplog.records[0].message == "OpenHighlightBanner"
        assert caplog.records[0].extra == {
            "analyticsSource": "adage",
            "queryId": "1234a",
            "from": "search",
            "userId": get_hashed_user_id(EMAIL),
            "uai": UAI,
            "user_role": AdageFrontRoles.READONLY,
            "banner": "TFMAC-2025",
        }
