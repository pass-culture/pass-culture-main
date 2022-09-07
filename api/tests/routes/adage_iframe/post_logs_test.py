import logging

from tests.routes.adage_iframe.utils_create_test_token import create_adage_valid_token_with_email


class PostLogsTests:
    def test_log_catalog_view(self, client, caplog):
        # given
        adage_jwt_fake_valid_token = create_adage_valid_token_with_email(email="test@mail.com")
        client.auth_header = {"Authorization": f"Bearer {adage_jwt_fake_valid_token}"}

        # when
        with caplog.at_level(logging.INFO):
            response = client.post("/adage-iframe/logs/catalog-view", json={})

        # then
        assert response.status_code == 204
        assert caplog.records[0].message == "CatalogView"
        assert caplog.records[0].extra == {
            "analyticsSource": "adage",
            "userId": "f0e2a21bcf499cbc713c47d8f034d66e90a99f9ffcfe96466c9971dfdc5c9816",
            "source": "homepage",
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
            "resultsCount": 0,
        }

    def test_log_offer_detail(self, client, caplog):
        # given
        adage_jwt_fake_valid_token = create_adage_valid_token_with_email(email="test@mail.com")
        client.auth_header = {"Authorization": f"Bearer {adage_jwt_fake_valid_token}"}

        # when
        with caplog.at_level(logging.INFO):
            response = client.post("/adage-iframe/logs/offer-detail", json={"stockId": 1})

        # then
        assert response.status_code == 204
        assert caplog.records[0].message == "OfferDetailButtonClick"
        assert caplog.records[0].extra == {
            "analyticsSource": "adage",
            "stockId": 1,
            "userId": "f0e2a21bcf499cbc713c47d8f034d66e90a99f9ffcfe96466c9971dfdc5c9816",
        }

    def test_log_offer_template_details_button_click(self, client, caplog):
        # given
        adage_jwt_fake_valid_token = create_adage_valid_token_with_email(email="test@mail.com")
        client.auth_header = {"Authorization": f"Bearer {adage_jwt_fake_valid_token}"}

        # when
        with caplog.at_level(logging.INFO):
            response = client.post("/adage-iframe/logs/offer-template-detail", json={"offerId": 1})

        # then
        assert response.status_code == 204
        assert caplog.records[0].message == "TemplateOfferDetailButtonClick"
        assert caplog.records[0].extra == {
            "analyticsSource": "adage",
            "offerId": 1,
            "userId": "f0e2a21bcf499cbc713c47d8f034d66e90a99f9ffcfe96466c9971dfdc5c9816",
        }

    def test_log_booking_modal_button_click(self, client, caplog):
        # given
        adage_jwt_fake_valid_token = create_adage_valid_token_with_email(email="test@mail.com")
        client.auth_header = {"Authorization": f"Bearer {adage_jwt_fake_valid_token}"}

        # when
        with caplog.at_level(logging.INFO):
            response = client.post("/adage-iframe/logs/booking-modal-button", json={"stockId": 1})

        # then
        assert response.status_code == 204
        assert caplog.records[0].message == "BookingModalButtonClick"
        assert caplog.records[0].extra == {
            "analyticsSource": "adage",
            "stockId": 1,
            "userId": "f0e2a21bcf499cbc713c47d8f034d66e90a99f9ffcfe96466c9971dfdc5c9816",
        }

    def test_log_contact_modal_button_click(self, client, caplog):
        # given
        adage_jwt_fake_valid_token = create_adage_valid_token_with_email(email="test@mail.com")
        client.auth_header = {"Authorization": f"Bearer {adage_jwt_fake_valid_token}"}

        # when
        with caplog.at_level(logging.INFO):
            response = client.post("/adage-iframe/logs/offer-template-detail", json={"offerId": 1})

        # then
        assert response.status_code == 204
        assert caplog.records[0].message == "ContactModalButtonClick"
        assert caplog.records[0].extra == {
            "analyticsSource": "adage",
            "offerId": 1,
            "userId": "f0e2a21bcf499cbc713c47d8f034d66e90a99f9ffcfe96466c9971dfdc5c9816",
        }
