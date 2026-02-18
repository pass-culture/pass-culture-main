import datetime

import pytest

from pcapi.core import testing
from pcapi.core.educational import factories
from pcapi.core.educational import models
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.providers import factories as provider_factories
from pcapi.models.offer_mixin import OfferValidationStatus
from pcapi.utils.date import get_naive_utc_now

from tests.routes.public.helpers import PublicAPIEndpointBaseHelper


@pytest.mark.usefixtures("db_session")
class CollectiveOffersPublicGetOfferTest(PublicAPIEndpointBaseHelper):
    endpoint_url = "/v2/collective/offers/"
    endpoint_method = "get"

    num_queries = 1  # select api_key, offerer and provider
    num_queries += 1  # select offers and bookings

    def test_get_offers(self, client):
        venue_provider = provider_factories.VenueProviderFactory()

        offerers_factories.ApiKeyFactory(provider=venue_provider.provider)

        stock1 = factories.CollectiveStockFactory(collectiveOffer__provider=venue_provider.provider)
        offer1 = stock1.collectiveOffer

        offer2 = factories.CollectiveBookingFactory(
            collectiveStock__collectiveOffer__provider=venue_provider.provider
        ).collectiveStock.collectiveOffer
        booking2 = offer2.collectiveStock.collectiveBookings[0]

        with testing.assert_num_queries(self.num_queries):
            response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).get(
                "/v2/collective/offers/"
            )
            assert response.status_code == 200

        assert response.json == [
            {
                "id": offer1.id,
                "venueId": offer1.venueId,
                "startDatetime": stock1.startDatetime.isoformat(timespec="seconds"),
                "endDatetime": stock1.endDatetime.isoformat(timespec="seconds"),
                "offerStatus": offer1.displayedStatus.value,
                "bookings": [],
            },
            {
                "id": offer2.id,
                "venueId": offer2.venueId,
                "startDatetime": offer2.collectiveStock.startDatetime.isoformat(timespec="seconds"),
                "endDatetime": offer2.collectiveStock.endDatetime.isoformat(timespec="seconds"),
                "offerStatus": offer2.displayedStatus.value,
                "bookings": [
                    {
                        "id": booking2.id,
                        "status": booking2.status.value,
                        "confirmationDate": (
                            booking2.confirmationDate.isoformat() if booking2.confirmationDate else None
                        ),
                        "cancellationLimitDate": (
                            booking2.cancellationLimitDate.isoformat() if booking2.cancellationLimitDate else None
                        ),
                        "reimbursementDate": (
                            booking2.reimbursementDate.isoformat() if booking2.reimbursementDate else None
                        ),
                        "dateUsed": booking2.dateUsed.isoformat() if booking2.dateUsed else None,
                        "dateCreated": booking2.dateCreated.isoformat() if booking2.dateCreated else None,
                    }
                ],
            },
        ]

    @pytest.mark.parametrize(
        "status",
        set(models.CollectiveOfferDisplayedStatus)
        - {
            models.CollectiveOfferDisplayedStatus.HIDDEN,
            models.CollectiveOfferDisplayedStatus.DRAFT,
            models.CollectiveOfferDisplayedStatus.ARCHIVED,
        },
    )
    def test_displayed_status_filter(self, client, status):
        venue_provider = provider_factories.VenueProviderFactory()
        offerers_factories.ApiKeyFactory(provider=venue_provider.provider)

        offer = factories.create_collective_offer_by_status(status=status, provider=venue_provider.provider)

        # add an offer with another status that will not be present in the result
        other_status = next((s for s in models.CollectiveOfferDisplayedStatus if s != status))
        factories.create_collective_offer_by_status(status=other_status, provider=venue_provider.provider)

        with testing.assert_num_queries(self.num_queries):
            response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).get(
                f"/v2/collective/offers/?offerStatus={status.value}"
            )

        assert response.status_code == 200
        [response_offer] = response.json
        assert response_offer["id"] == offer.id
        assert response_offer["offerStatus"] == status.value

    def test_displayed_status_filter_archived(self, client):
        venue_provider = provider_factories.VenueProviderFactory()
        offerers_factories.ApiKeyFactory(provider=venue_provider.provider)

        offer = factories.create_collective_offer_by_status(
            status=models.CollectiveOfferDisplayedStatus.ARCHIVED, provider=venue_provider.provider
        )
        factories.CollectiveStockFactory(collectiveOffer=offer)

        with testing.assert_num_queries(self.num_queries):
            response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).get(
                "/v2/collective/offers/?offerStatus=ARCHIVED"
            )

        assert response.status_code == 200
        [response_offer] = response.json
        assert response_offer["id"] == offer.id
        assert response_offer["offerStatus"] == "ARCHIVED"

    def test_no_offers(self, client):
        venue_provider = provider_factories.VenueProviderFactory()

        offerers_factories.ApiKeyFactory(provider=venue_provider.provider)

        client = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY)
        with testing.assert_num_queries(self.num_queries):
            response = client.get("/v2/collective/offers/")
            assert response.status_code == 200

        assert not response.json

    def test_filter_date(self):
        plain_api_key, provider = self.setup_provider()
        venue_provider = provider_factories.VenueProviderFactory(provider=provider)

        now = get_naive_utc_now()
        stock = factories.CollectiveStockFactory(collectiveOffer__provider=venue_provider.provider, startDatetime=now)

        # beginning filter after event start
        query_date = now + datetime.timedelta(days=1)
        with testing.assert_num_queries(self.num_queries):
            response = self.make_request(
                plain_api_key=plain_api_key, query_params={"periodBeginningDate": query_date.isoformat()}
            )

        assert response.status_code == 200
        assert response.json == []

        # ending filter before event start
        query_date = now - datetime.timedelta(days=1)
        with testing.assert_num_queries(self.num_queries):
            response = self.make_request(
                plain_api_key=plain_api_key, query_params={"periodEndingDate": query_date.isoformat()}
            )

        assert response.status_code == 200
        assert response.json == []

        # beginning filter before event start
        query_date = now - datetime.timedelta(days=1)
        with testing.assert_num_queries(self.num_queries):
            response = self.make_request(
                plain_api_key=plain_api_key, query_params={"periodBeginningDate": query_date.isoformat()}
            )

        assert response.status_code == 200
        [offer] = response.json
        assert offer["id"] == stock.collectiveOfferId

        # ending filter after event start
        query_date = now + datetime.timedelta(days=1)
        with testing.assert_num_queries(self.num_queries):
            response = self.make_request(
                plain_api_key=plain_api_key, query_params={"periodEndingDate": query_date.isoformat()}
            )

        assert response.status_code == 200
        [offer] = response.json
        assert offer["id"] == stock.collectiveOfferId

    def test_offer_without_stock(self, client):
        venue_provider = provider_factories.VenueProviderFactory()

        offerers_factories.ApiKeyFactory(provider=venue_provider.provider)
        stock = factories.CollectiveStockFactory(collectiveOffer__provider=venue_provider.provider)
        offer = stock.collectiveOffer

        # this offer without stock will not appear in the result
        factories.CollectiveOfferFactory(provider=venue_provider.provider)

        client = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY)
        with testing.assert_num_queries(self.num_queries):
            response = client.get("/v2/collective/offers/")
            assert response.status_code == 200

        assert response.json == [
            {
                "id": offer.id,
                "venueId": offer.venueId,
                "startDatetime": stock.startDatetime.isoformat(timespec="seconds"),
                "endDatetime": stock.endDatetime.isoformat(timespec="seconds"),
                "offerStatus": "PUBLISHED",
                "bookings": [],
            },
        ]

    def test_other_offerer_offers_not_visible(self, client):
        venue_provider = provider_factories.VenueProviderFactory()

        offerers_factories.ApiKeyFactory(provider=venue_provider.provider)

        stock1 = factories.CollectiveStockFactory(collectiveOffer__provider=venue_provider.provider)
        offer1 = stock1.collectiveOffer

        venue_provider2 = provider_factories.VenueProviderFactory()
        factories.CollectiveStockFactory(collectiveOffer__provider=venue_provider2.provider)

        client = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY)
        with testing.assert_num_queries(self.num_queries):
            response = client.get("/v2/collective/offers/")
            assert response.status_code == 200

        assert response.json == [
            {
                "id": offer1.id,
                "venueId": offer1.venueId,
                "startDatetime": stock1.startDatetime.isoformat(timespec="seconds"),
                "endDatetime": stock1.endDatetime.isoformat(timespec="seconds"),
                "offerStatus": "PUBLISHED",
                "bookings": [],
            },
        ]

    def test_draft_offers_not_visible(self, client):
        venue_provider = provider_factories.VenueProviderFactory()

        offerers_factories.ApiKeyFactory(provider=venue_provider.provider)

        stock1 = factories.CollectiveStockFactory(collectiveOffer__provider=venue_provider.provider)
        offer1 = stock1.collectiveOffer
        factories.CollectiveStockFactory(
            collectiveOffer__provider=venue_provider.provider,
            collectiveOffer__validation=OfferValidationStatus.DRAFT,
        )

        client = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY)
        with testing.assert_num_queries(self.num_queries):
            response = client.get("/v2/collective/offers/")
            assert response.status_code == 200

        assert response.json == [
            {
                "id": offer1.id,
                "venueId": offer1.venueId,
                "startDatetime": stock1.startDatetime.isoformat(timespec="seconds"),
                "endDatetime": stock1.endDatetime.isoformat(timespec="seconds"),
                "offerStatus": "PUBLISHED",
                "bookings": [],
            },
        ]

    def test_user_did_not_create_offer_using_the_api(self, client):
        """Ensure that a user cannot fetch an offer that he did not
        created with the API"""
        venue_provider = provider_factories.VenueProviderFactory()
        offerers_factories.ApiKeyFactory(provider=venue_provider.provider)

        offer_id = factories.CollectiveStockFactory().collectiveOffer.id

        api_client = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY)
        with testing.assert_num_queries(self.num_queries + 2):  # double rollback
            response = api_client.get(f"/v2/collective/offers/{offer_id}")
            assert response.status_code == 403

    @pytest.mark.parametrize(
        "query_params,expected_json",
        (
            (
                {"offerStatus": "BLOUP"},
                {
                    "offerStatus": [
                        "value is not a valid enumeration member; permitted: "
                        "'PUBLISHED', 'UNDER_REVIEW', 'REJECTED', 'PREBOOKED', "
                        "'BOOKED', 'HIDDEN', 'EXPIRED', 'ENDED', 'CANCELLED', "
                        "'REIMBURSED', 'ARCHIVED', 'DRAFT'"
                    ]
                },
            ),
            ({"venueId": "BLOUP"}, {"venueId": ["value is not a valid integer"]}),
            ({"periodBeginningDate": "BLOUP"}, {"periodBeginningDate": ["invalid datetime format"]}),
            ({"periodEndingDate": "2024-05 -10T15:00:00+02:00"}, {"periodEndingDate": ["invalid datetime format"]}),
        ),
    )
    def test_invalid_query_params(self, query_params, expected_json):
        plain_api_key, _ = self.setup_provider()

        with testing.assert_num_queries(3):  # provider + double rollback
            response = self.make_request(plain_api_key=plain_api_key, query_params=query_params)

        assert response.status_code == 400
        assert response.json == expected_json
