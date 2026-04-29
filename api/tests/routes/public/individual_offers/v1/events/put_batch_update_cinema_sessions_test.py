import datetime

import pytest
import time_machine

from pcapi.core.geography import factories as geography_factories
from pcapi.utils import date as date_utils

from tests.routes.public.helpers import PublicAPIVenueEndpointHelper


def _get_stock_payload(partial_payload: dict | None = None) -> dict:
    two_weeks_from_now = date_utils.get_naive_utc_now().replace(second=0, microsecond=0) + datetime.timedelta(weeks=2)
    payload = {
        "beginningDatetime": date_utils.format_into_utc_date(two_weeks_from_now),
        "priceCategoryIdAtProvider": "PC",
        "quantity": 100,
        "idAtProvider": "film1234567_session1",
        "features": ["VF"],
    }
    if partial_payload:
        payload.update(**partial_payload)
    return payload


@pytest.mark.usefixtures("db_session")
class PutCinemaSessionsTest(PublicAPIVenueEndpointHelper):
    endpoint_url = "/public/offers/v1/events/cinema_sessions"
    endpoint_method = "put"

    @staticmethod
    def _get_base_payload(venue_id: int) -> dict:
        return {
            "venueId": venue_id,
            "offers": [
                {
                    "filmId": "allocine_id:1000015954",  # Juste une illusion
                    "priceCategories": [{"price": 500, "label": "Tarif pass Culture", "idAtProvider": "PC"}],
                    "stocks": [(_get_stock_payload())],
                }
            ],
        }

    ### 404 errors

    def test_should_raise_404_because_has_no_access_to_venue(self):
        plain_api_key, _ = self.setup_provider()
        venue = self.setup_venue()
        response = self.make_request(plain_api_key, json_body=self._get_base_payload(venue.id))
        assert response.status_code == 404

    def test_should_raise_404_because_venue_provider_is_inactive(self):
        plain_api_key, venue_provider = self.setup_inactive_venue_provider()
        response = self.make_request(plain_api_key, json_body=self._get_base_payload(venue_provider.venueId))
        assert response.status_code == 404

    def test_should_raise_404_because_venue_does_not_exist(self):
        plain_api_key, _ = self.setup_provider()
        response = self.make_request(plain_api_key, json_body=self._get_base_payload(1))
        assert response.status_code == 404

    def test_should_raise_404_because_address_does_not_exist(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        payload = self._get_base_payload(venue_provider.venueId)
        payload["offers"][0]["address"] = {"id": 1, "label": "Quelque part"}

        response = self.make_request(plain_api_key, json_body=payload)
        assert response.status_code == 404
        assert response.json == {"offers.0.address.id": ["Address not found"]}

    ### 400 errors (serializer)

    @pytest.mark.parametrize(
        "film_id, expected_response_json",
        [
            ("allocineid:1234567", {"offers.0.filmId": ["String should match pattern '^(visa|allocine_id)\\:[0-9]+'"]}),
            ("allocine_id:aa", {"offers.0.filmId": ["String should match pattern '^(visa|allocine_id)\\:[0-9]+'"]}),
            (1234567, {"offers.0.filmId": ["Input should be a valid string"]}),
            (
                "allocine_id:" + 100 * "1",
                {"offers.0.filmId": ["String should have at most 100 characters"]},
            ),
        ],
    )
    def test_should_raise_400_because_offer_filmId_is_incorrect(self, film_id, expected_response_json):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        payload = self._get_base_payload(venue_provider.venueId)
        payload["offers"][0]["filmId"] = film_id

        response = self.make_request(plain_api_key, json_body=payload)
        assert response.status_code == 400
        assert response.json == expected_response_json

    @pytest.mark.parametrize(
        "price_categories, expected_response_json",
        [
            ([], {"offers.0.priceCategories": ["List should have at least 1 item after validation, not 0"]}),
            # checks on idAtProvider
            (
                [{"price": 500, "label": "Tarif pass Culture"}],
                {"offers.0.priceCategories.0.idAtProvider": ["Field required"]},
            ),
            (
                [{"price": 500, "label": "Tarif pass Culture", "idAtProvider": 1234}],
                {"offers.0.priceCategories.0.idAtProvider": ["Input should be a valid string"]},
            ),
            (
                [
                    {"price": 500, "label": "Tarif pass Culture", "idAtProvider": "1234"},
                    {"price": 1500, "label": "Tarif normal", "idAtProvider": "1234"},
                ],
                {"offers.0.priceCategories": ['`idAtProvider` "1234" is duplicated']},
            ),
            (
                [{"price": 500, "label": "Tarif pass Culture", "idAtProvider": "a" * 71}],
                {"offers.0.priceCategories.0.idAtProvider": ["String should have at most 70 characters"]},
            ),
            # checks on price
            (
                [{"label": "Tarif pass Culture", "idAtProvider": "1234"}],
                {"offers.0.priceCategories.0.price": ["Field required"]},
            ),
            (
                [{"price": "10€ tout rond", "label": "Tarif pass Culture", "idAtProvider": "1234"}],
                {
                    "offers.0.priceCategories.0.price": [
                        "Input should be a valid integer, unable to parse string as an integer"
                    ]
                },
            ),
            (
                [{"price": 1.3, "label": "Tarif pass Culture", "idAtProvider": "1234"}],
                {
                    "offers.0.priceCategories.0.price": [
                        "Input should be a valid integer, got a number with a fractional part"
                    ]
                },
            ),
            (
                [{"price": -1, "label": "Tarif pass Culture", "idAtProvider": "1234"}],
                {"offers.0.priceCategories.0.price": ["Input should be greater than or equal to 0"]},
            ),
            (
                [{"price": 30001, "label": "Tarif pass Culture", "idAtProvider": "1234"}],
                {"offers.0.priceCategories.0.price": ["Input should be less than or equal to 30000"]},
            ),
            # checks on label
            (
                [{"price": 500, "idAtProvider": "PC"}],
                {"offers.0.priceCategories.0.label": ["Field required"]},
            ),
            (
                [{"price": 500, "label": 1, "idAtProvider": "PC"}],
                {"offers.0.priceCategories.0.label": ["Input should be a valid string"]},
            ),
            (
                [{"price": 500, "label": "a" * 51, "idAtProvider": "PC"}],
                {"offers.0.priceCategories.0.label": ["String should have at most 50 characters"]},
            ),
        ],
    )
    def test_should_raise_400_because_offer_priceCategories_is_incorrect(
        self, price_categories, expected_response_json
    ):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        payload = self._get_base_payload(venue_provider.venueId)
        payload["offers"][0]["priceCategories"] = price_categories

        response = self.make_request(plain_api_key, json_body=payload)
        assert response.status_code == 400
        assert response.json == expected_response_json

    @time_machine.travel(datetime.datetime(2025, 6, 27), tick=False)
    @pytest.mark.parametrize(
        "stocks, expected_response_json",
        [
            ([], {"offers.0.stocks": ["List should have at least 1 item after validation, not 0"]}),
            (
                [{}],
                {
                    "offers.0.stocks.0.beginningDatetime": ["Field required"],
                    "offers.0.stocks.0.features": ["Field required"],
                    "offers.0.stocks.0.idAtProvider": ["Field required"],
                    "offers.0.stocks.0.priceCategoryIdAtProvider": ["Field required"],
                    "offers.0.stocks.0.quantity": ["Field required"],
                },
            ),
            # checks on `beginningDatetime`
            (
                [_get_stock_payload({"beginningDatetime": "1999-01-01T15:59:59+04:00"})],
                {"offers.0.stocks.0.beginningDatetime": ["The datetime must be in the future."]},
            ),
            (
                [_get_stock_payload({"beginningDatetime": "2025-06-28T15:59:00"})],
                {"offers.0.stocks.0.beginningDatetime": ["The datetime must be timezone-aware."]},
            ),
            # checks on `quantity`
            (
                [_get_stock_payload({"quantity": "coucou"})],
                {
                    "offers.0.stocks.0.quantity": [
                        "Input should be a valid integer, unable to parse string as an integer"
                    ]
                },
            ),
            (
                [_get_stock_payload({"quantity": 12.3})],
                {
                    "offers.0.stocks.0.quantity": [
                        "Input should be a valid integer, got a number with a fractional part"
                    ]
                },
            ),
            # checks on `features`
            (
                [_get_stock_payload({"features": []})],
                {"offers.0.stocks.0.features": ["You must indicate if cinema session is in `VF` or in `VO`"]},
            ),
            (
                [_get_stock_payload({"features": ["VF", "VO"]})],
                {"offers.0.stocks.0.features": ["The cinema session cannot be both in `VF` and in `VO`"]},
            ),
            (
                [_get_stock_payload({"features": ["COUCOUUUUUUUUU"]})],
                {"offers.0.stocks.0.features.0": ["Input should be 'VF', 'VO', '3D' or 'ICE'"]},
            ),
            # checks on `idAtProvider`
            (
                [_get_stock_payload(), _get_stock_payload()],
                {"offers.0.stocks": ['`idAtProvider` "film1234567_session1" is duplicated']},
            ),
            (
                [_get_stock_payload({"idAtProvider": 1234})],
                {"offers.0.stocks.0.idAtProvider": ["Input should be a valid string"]},
            ),
            (
                [_get_stock_payload({"idAtProvider": "a" * 71})],
                {"offers.0.stocks.0.idAtProvider": ["String should have at most 70 characters"]},
            ),
            # checks on `priceCategoryIdAtProvider`
            (
                [_get_stock_payload({"priceCategoryIdAtProvider": 1234})],
                {"offers.0.stocks.0.priceCategoryIdAtProvider": ["Input should be a valid string"]},
            ),
            (
                [_get_stock_payload({"priceCategoryIdAtProvider": "a" * 71})],
                {"offers.0.stocks.0.priceCategoryIdAtProvider": ["String should have at most 70 characters"]},
            ),
        ],
    )
    def test_should_raise_400_because_offer_stocks_is_incorrect(self, stocks, expected_response_json):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        payload = self._get_base_payload(venue_provider.venueId)
        payload["offers"][0]["stocks"] = stocks

        response = self.make_request(plain_api_key, json_body=payload)
        assert response.status_code == 400
        assert response.json == expected_response_json

    @pytest.mark.parametrize(
        "address, expected_response_json",
        [
            # checks on idAtProvider
            (
                {"label": "Mon cinéma dans le pré"},
                {"offers.0.address.id": ["Field required"]},
            ),
            (
                {"id": "coucou", "label": "Mon cinéma dans le pré"},
                {"offers.0.address.id": ["Input should be a valid integer, unable to parse string as an integer"]},
            ),
            # checks on label
            (
                {"id": 12, "label": 1234},
                {"offers.0.address.label": ["Input should be a valid string"]},
            ),
            (
                {"id": 12, "label": "a" * 201},
                {"offers.0.address.label": ["String should have at most 200 characters"]},
            ),
        ],
    )
    def test_should_raise_400_because_offer_address_is_incorrect(self, address, expected_response_json):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        payload = self._get_base_payload(venue_provider.venueId)
        payload["offers"][0]["address"] = address

        response = self.make_request(plain_api_key, json_body=payload)
        assert response.status_code == 400
        assert response.json == expected_response_json

    def test_should_raise_400_because_priceCategoryIdAtProvider_is_missing(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        payload = {
            "venueId": venue_provider.venueId,
            "offers": [
                {
                    "filmId": "allocine_id:1000015954",
                    "priceCategories": [{"price": 500, "label": "Tarif pass Culture", "idAtProvider": "PC"}],
                    "stocks": [
                        _get_stock_payload(),
                        _get_stock_payload({"priceCategoryIdAtProvider": "idNotFound", "idAtProvider": "bis"}),
                        _get_stock_payload(
                            {"priceCategoryIdAtProvider": "idNotFoundBis", "idAtProvider": "bisrepetitas"}
                        ),
                    ],
                }
            ],
        }

        response = self.make_request(plain_api_key, json_body=payload)
        assert response.status_code == 400
        assert response.json == {"offers.0": ["Missing `priceCategoryIdAtProvider`: idNotFound, idNotFoundBis"]}

    def test_should_raise_400_because_offers_contains_2_venue_offers_with_the_same_film_id(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        payload = {
            "venueId": venue_provider.venueId,
            "offers": [
                {
                    "filmId": "allocine_id:1000015954",
                    "priceCategories": [{"price": 500, "label": "Tarif pass Culture", "idAtProvider": "PC"}],
                    "stocks": [_get_stock_payload()],
                },
                {
                    "filmId": "allocine_id:1000015954",
                    "priceCategories": [{"price": 500, "label": "Tarif pass Culture", "idAtProvider": "PC"}],
                    "stocks": [_get_stock_payload()],
                },
            ],
        }

        response = self.make_request(plain_api_key, json_body=payload)
        assert response.status_code == 400, response.json
        assert response.json == {"offers": ['Film id "allocine_id:1000015954" is duplicated in payload']}

    def test_should_raise_400_because_offers_contains_2_address_offers_with_the_same_film_id(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        address = geography_factories.AddressFactory()
        payload = {
            "venueId": venue_provider.venueId,
            "offers": [
                {
                    "filmId": "allocine_id:1000015954",
                    "address": {"id": address.id, "label": "Un drive-in"},
                    "priceCategories": [{"price": 500, "label": "Tarif pass Culture", "idAtProvider": "PC"}],
                    "stocks": [_get_stock_payload()],
                },
                {
                    "filmId": "allocine_id:1000015954",
                    "address": {"id": address.id, "label": "Un drive-in"},
                    "priceCategories": [{"price": 500, "label": "Tarif pass Culture", "idAtProvider": "PC"}],
                    "stocks": [_get_stock_payload()],
                },
            ],
        }

        response = self.make_request(plain_api_key, json_body=payload)
        assert response.status_code == 400, response.json
        assert response.json == {
            "offers": [f'Film id "allocine_id:1000015954" is duplicated in payload for address {address.id}']
        }

    ### Success

    def test_should_return_204(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        response = self.make_request(plain_api_key, json_body=self._get_base_payload(venue_provider.venueId))
        assert response.status_code == 204

    def test_should_return_204_with_address(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        address = geography_factories.AddressFactory()
        payload = self._get_base_payload(venue_provider.venueId)
        payload["offers"][0]["address"] = {"id": address.id, "label": "Un drive-in"}
        response = self.make_request(plain_api_key, json_body=payload)
        assert response.status_code == 204

    def test_should_return_204_with_duplicated_features(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        payload = self._get_base_payload(venue_provider.venueId)
        payload["offers"][0]["stocks"] = [_get_stock_payload({"features": ["VF", "VF"]})]
        response = self.make_request(plain_api_key, json_body=payload)
        assert response.status_code == 204, response.json

    def test_should_return_204_with_duplicated_film_id_if_offers_are_at_different_location(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        address = geography_factories.AddressFactory()
        address2 = geography_factories.AddressFactory()
        payload = {
            "venueId": venue_provider.venueId,
            "offers": [
                {
                    "filmId": "allocine_id:1000015954",
                    "address": {"id": address.id, "label": "Un drive-in"},
                    "priceCategories": [{"price": 500, "label": "Tarif pass Culture", "idAtProvider": "PC"}],
                    "stocks": [_get_stock_payload()],
                },
                {
                    "filmId": "allocine_id:1000015954",
                    "address": {"id": address2.id, "label": "Une salle des fêtes"},
                    "priceCategories": [{"price": 500, "label": "Tarif pass Culture", "idAtProvider": "PC"}],
                    "stocks": [_get_stock_payload()],
                },
            ],
        }

        response = self.make_request(plain_api_key, json_body=payload)
        assert response.status_code == 204, response.json

    def test_should_return_204_with_duplicated_film_id_if_offers_are_at_different_location_2(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        address = geography_factories.AddressFactory()
        payload = {
            "venueId": venue_provider.venueId,
            "offers": [
                {  # offer located at venue address
                    "filmId": "allocine_id:1000015954",
                    "priceCategories": [{"price": 500, "label": "Tarif pass Culture", "idAtProvider": "PC"}],
                    "stocks": [_get_stock_payload()],
                },
                {  # offer located at different address
                    "filmId": "allocine_id:1000015954",
                    "address": {"id": address.id, "label": "Un drive-in"},
                    "priceCategories": [{"price": 500, "label": "Tarif pass Culture", "idAtProvider": "PC"}],
                    "stocks": [_get_stock_payload()],
                },
            ],
        }

        response = self.make_request(plain_api_key, json_body=payload)
        assert response.status_code == 204, response.json

    def test_should_return_204_with_several_priceCategories(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        payload = {
            "venueId": venue_provider.venueId,
            "offers": [
                {
                    "filmId": "allocine_id:1000015954",
                    "priceCategories": [
                        {"price": 500, "label": "Tarif pass Culture", "idAtProvider": "PC"},
                        {"price": 550, "label": "Tarif pass Culture (premium)", "idAtProvider": "PC_premium"},
                    ],
                    "stocks": [
                        _get_stock_payload(),
                        _get_stock_payload({"priceCategoryIdAtProvider": "PC_premium", "idAtProvider": "bis"}),
                    ],
                }
            ],
        }
        response = self.make_request(plain_api_key, json_body=payload)
        assert response.status_code == 204, response.json
