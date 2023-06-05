import logging

from tests.routes.adage_iframe.utils_create_test_token import create_adage_valid_token_with_email


class PostLogsTest:
    def test_log_catalog_view(self, client, caplog):
        # given
        adage_jwt_fake_valid_token = create_adage_valid_token_with_email(email="test@mail.com")
        client.auth_header = {"Authorization": f"Bearer {adage_jwt_fake_valid_token}"}

        # when
        with caplog.at_level(logging.INFO):
            response = client.post(
                "/adage-iframe/logs/catalog-view",
                json={"source": "partnersMap", "AdageHeaderFrom": "for_my_institution"},
            )

        # then
        assert response.status_code == 204
        assert caplog.records[0].message == "CatalogView"
        assert caplog.records[0].extra == {
            "analyticsSource": "adage",
            "source": "partnersMap",
            "AdageHeaderFrom": "for_my_institution",
            "userId": "f0e2a21bcf499cbc713c47d8f034d66e90a99f9ffcfe96466c9971dfdc5c9816",
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
                    "AdageHeaderFrom": "for_my_institution",
                    "resultsCount": 0,
                },
            )

        # then
        assert response.status_code == 204
        assert caplog.records[0].message == "SearchButtonClicked"
        assert caplog.records[0].extra == {
            "analyticsSource": "adage",
            "userId": "f0e2a21bcf499cbc713c47d8f034d66e90a99f9ffcfe96466c9971dfdc5c9816",
            "filters": [
                "departments",
                "institutionId",
            ],
            "AdageHeaderFrom": "for_my_institution",
            "resultsCount": 0,
        }

    def test_log_offer_detail(self, client, caplog):
        # given
        adage_jwt_fake_valid_token = create_adage_valid_token_with_email(email="test@mail.com")
        client.auth_header = {"Authorization": f"Bearer {adage_jwt_fake_valid_token}"}

        # when
        with caplog.at_level(logging.INFO):
            response = client.post(
                "/adage-iframe/logs/offer-detail",
                json={"stockId": 1, "AdageHeaderFrom": "for_my_institution"},
            )

        # then
        assert response.status_code == 204
        assert caplog.records[0].message == "OfferDetailButtonClick"
        assert caplog.records[0].extra == {
            "analyticsSource": "adage",
            "stockId": 1,
            "AdageHeaderFrom": "for_my_institution",
            "userId": "f0e2a21bcf499cbc713c47d8f034d66e90a99f9ffcfe96466c9971dfdc5c9816",
        }

    def test_log_offer_template_details_button_click(self, client, caplog):
        # given
        adage_jwt_fake_valid_token = create_adage_valid_token_with_email(email="test@mail.com")
        client.auth_header = {"Authorization": f"Bearer {adage_jwt_fake_valid_token}"}

        # when
        with caplog.at_level(logging.INFO):
            response = client.post(
                "/adage-iframe/logs/offer-template-detail",
                json={"offerId": 1, "AdageHeaderFrom": "for_my_institution"},
            )

        # then
        assert response.status_code == 204
        assert caplog.records[0].message == "TemplateOfferDetailButtonClick"
        assert caplog.records[0].extra == {
            "analyticsSource": "adage",
            "offerId": 1,
            "AdageHeaderFrom": "for_my_institution",
            "userId": "f0e2a21bcf499cbc713c47d8f034d66e90a99f9ffcfe96466c9971dfdc5c9816",
        }

    def test_log_booking_modal_button_click(self, client, caplog):
        # given
        adage_jwt_fake_valid_token = create_adage_valid_token_with_email(email="test@mail.com")
        client.auth_header = {"Authorization": f"Bearer {adage_jwt_fake_valid_token}"}

        # when
        with caplog.at_level(logging.INFO):
            response = client.post(
                "/adage-iframe/logs/booking-modal-button",
                json={"stockId": 1, "AdageHeaderFrom": "for_my_institution"},
            )

        # then
        assert response.status_code == 204
        assert caplog.records[0].message == "BookingModalButtonClick"
        assert caplog.records[0].extra == {
            "analyticsSource": "adage",
            "stockId": 1,
            "AdageHeaderFrom": "for_my_institution",
            "userId": "f0e2a21bcf499cbc713c47d8f034d66e90a99f9ffcfe96466c9971dfdc5c9816",
        }

    def test_log_contact_modal_button_click(self, client, caplog):
        # given
        adage_jwt_fake_valid_token = create_adage_valid_token_with_email(email="test@mail.com")
        client.auth_header = {"Authorization": f"Bearer {adage_jwt_fake_valid_token}"}

        # when
        with caplog.at_level(logging.INFO):
            response = client.post(
                "/adage-iframe/logs/offer-template-detail",
                json={"offerId": 1, "AdageHeaderFrom": "for_my_institution"},
            )

        # then
        assert response.status_code == 204
        assert caplog.records[0].message == "TemplateOfferDetailButtonClick"
        assert caplog.records[0].extra == {
            "analyticsSource": "adage",
            "offerId": 1,
            "AdageHeaderFrom": "for_my_institution",
            "userId": "f0e2a21bcf499cbc713c47d8f034d66e90a99f9ffcfe96466c9971dfdc5c9816",
        }

    def test_log_fav_offer_button_click(self, client, caplog):
        # given
        adage_jwt_fake_valid_token = create_adage_valid_token_with_email(email="test@mail.com")
        client.auth_header = {"Authorization": f"Bearer {adage_jwt_fake_valid_token}"}

        # when
        with caplog.at_level(logging.INFO):
            response = client.post(
                "/adage-iframe/logs/fav-offer",
                json={"offerId": 1, "AdageHeaderFrom": "for_my_institution"},
            )

        # then
        assert response.status_code == 204
        assert caplog.records[0].message == "FavOfferButtonClick"
        assert caplog.records[0].extra == {
            "analyticsSource": "adage",
            "offerId": 1,
            "AdageHeaderFrom": "for_my_institution",
            "userId": "f0e2a21bcf499cbc713c47d8f034d66e90a99f9ffcfe96466c9971dfdc5c9816",
        }

    def test_log_header_link_click(self, client, caplog):
        # given
        test_client = client.with_adage_token(email="test@mail.com", uai="123456")

        # when
        with caplog.at_level(logging.INFO):
            response = test_client.post(
                "/adage-iframe/logs/header-link-click",
                json={"header_link_name": "search", "AdageHeaderFrom": "for_my_institution"},
            )

        # then
        assert response.status_code == 204
        record = next(record for record in caplog.records if record.message == "HeaderLinkClick")

        assert record is not None
        assert record.extra == {
            "analyticsSource": "adage",
            "header_link_name": "search",
            "AdageHeaderFrom": "for_my_institution",
            "userId": "f0e2a21bcf499cbc713c47d8f034d66e90a99f9ffcfe96466c9971dfdc5c9816",
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
                    "AdageHeaderFrom": "for_my_institution",
                },
            )

        # then
        assert response.status_code == 204
        record = [record for record in caplog.records if record.message == "RequestPopinDismiss"][0]
        assert record.extra == {
            "analyticsSource": "adage",
            "collectiveOfferTemplateId": 1,
            "phoneNumber": "0601020304",
            "requestedDate": "2022-12-02",
            "totalStudents": 30,
            "totalTeachers": 2,
            "comment": "La première règle du Fight Club est: il est interdit de parler du Fight Club",
            "AdageHeaderFrom": "for_my_institution",
            "userId": "f0e2a21bcf499cbc713c47d8f034d66e90a99f9ffcfe96466c9971dfdc5c9816",
        }
