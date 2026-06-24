import pytest

import pcapi.core.artist.factories as artists_factories
import pcapi.core.chronicles.factories as chronicles_factories
import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offers.factories as offers_factories
from pcapi.core.artist.models import ArtistType
from pcapi.core.categories import subcategories
from pcapi.core.offers.models import ImageType
from pcapi.core.testing import assert_num_queries
from pcapi.models.offer_mixin import OfferValidationStatus
from pcapi.utils import date as date_utils


pytestmark = pytest.mark.usefixtures("db_session")


class OffersV4Test:
    # 1. select offer (+ joined venue/offerer, product, artistOfferLinks, headlineOffers, metaData, provider)
    # 2. select stocks (selectinload)
    base_num_queries = 2
    num_queries_with_product = 1  # select product.artistLinks (selectinload)

    def test_get_thing_offer(self, client):
        offer = offers_factories.OfferFactory(venue__isPermanent=True, subcategoryId=subcategories.CARTE_MUSEE.id)
        offers_factories.ThingStockFactory(offer=offer, price=12.34)

        offer_id = offer.id
        with assert_num_queries(self.base_num_queries):
            response = client.get(f"/native/v4/offer/{offer_id}")

        assert response.status_code == 200
        assert response.json["id"] == offer.id
        assert response.json["name"] == offer.name
        assert response.json["subcategoryId"] == "CARTE_MUSEE"
        assert response.json["isEvent"] is False
        assert response.json["isEducational"] is False

    def test_response_is_slim(self, client):
        # sections moved to dedicated sub-routes must NOT be in the main payload
        offer = offers_factories.OfferFactory()
        offers_factories.ThingStockFactory(offer=offer)

        response = client.get(f"/native/v4/offer/{offer.id}")

        assert response.status_code == 200
        for moved_key in (
            "venue",
            "address",
            "accessibility",
            "description",
            "withdrawalDetails",
            "images",
            "image",
            "metadata",
            "reactionsCount",
            "chronicles",
            "chroniclesCount",
            "proAdvicesCount",
            "stocks",
        ):
            assert moved_key not in response.json

    def test_get_event_offer_flags(self, client):
        offer = offers_factories.EventOfferFactory(subcategoryId=subcategories.SEANCE_CINE.id, isDuo=True)
        offers_factories.EventStockFactory(offer=offer, price=12.34, quantity=2)

        offer_id = offer.id
        with assert_num_queries(self.base_num_queries):
            response = client.get(f"/native/v4/offer/{offer_id}")

        assert response.status_code == 200
        assert response.json["isDuo"] is True
        assert response.json["isEvent"] is True

    def test_get_offer_with_artists(self, client):
        product = offers_factories.ProductFactory()
        offer = offers_factories.OfferFactory(product=product)
        offers_factories.ThingStockFactory(offer=offer)
        artist = artists_factories.ArtistFactory()
        blacklisted = artists_factories.ArtistFactory(is_blacklisted=True)
        artists_factories.ArtistProductLinkFactory(
            artist_id=artist.id, product_id=product.id, artist_type=ArtistType.PERFORMER
        )
        artists_factories.ArtistProductLinkFactory(artist_id=blacklisted.id, product_id=product.id)

        offer_id = offer.id
        with assert_num_queries(self.base_num_queries + self.num_queries_with_product):
            response = client.get(f"/native/v4/offer/{offer_id}")

        assert response.status_code == 200
        assert len(response.json["artists"]) == 1
        assert response.json["artists"][0]["id"] == artist.id
        assert response.json["artists"][0]["name"] == artist.name
        assert response.json["artists"][0]["role"] == ArtistType.PERFORMER.value

    def test_product_less_offer_duration_minutes(self, client):
        # _durationMinutes is eagerly loaded to avoid a lazy load on product-less offers
        offer = offers_factories.OfferFactory(durationMinutes=33)
        offers_factories.ThingStockFactory(offer=offer)

        offer_id = offer.id
        with assert_num_queries(self.base_num_queries):
            response = client.get(f"/native/v4/offer/{offer_id}")

        assert response.status_code == 200
        assert response.json["extraData"]["durationMinutes"] == 33

    def test_active_validated_offerer_offer_is_released(self, client):
        offer = offers_factories.OfferFactory()
        offers_factories.ThingStockFactory(offer=offer)

        offer_id = offer.id
        with assert_num_queries(self.base_num_queries):
            response = client.get(f"/native/v4/offer/{offer_id}")

        assert response.status_code == 200
        assert response.json["isReleased"] is True

    def test_closed_offerer_offer_is_not_released(self, client):
        offer = offers_factories.EventOfferFactory(venue__managingOfferer=offerers_factories.ClosedOffererFactory())
        offers_factories.EventStockFactory(offer=offer)

        offer_id = offer.id
        with assert_num_queries(self.base_num_queries):
            response = client.get(f"/native/v4/offer/{offer_id}")

        assert response.status_code == 200
        assert response.json["isReleased"] is False

    def test_get_offer_with_video(self, client):
        metadata = offers_factories.OfferMetaDataFactory(
            videoUrl="https://www.youtube.com/watch?v=fAkeV1ide0o",
            videoExternalId="fAkeV1ide0o",
            videoTitle="Test Video",
            videoThumbnailUrl="https://example.com/thumb.jpg",
            videoDuration=123,
        )
        offers_factories.ThingStockFactory(offer=metadata.offer)

        offer_id = metadata.offer.id
        with assert_num_queries(self.base_num_queries):
            response = client.get(f"/native/v4/offer/{offer_id}")

        assert response.status_code == 200
        assert response.json["video"] == {
            "id": "fAkeV1ide0o",
            "title": "Test Video",
            "thumbUrl": "https://example.com/thumb.jpg",
            "durationSeconds": 123,
        }

    def test_get_offer_not_found(self, client):
        # 1. select offer / 2. rollback / 3. rollback
        with assert_num_queries(3):
            response = client.get("/native/v4/offer/1")

        assert response.status_code == 404

    @pytest.mark.parametrize(
        "validation",
        [OfferValidationStatus.DRAFT, OfferValidationStatus.PENDING, OfferValidationStatus.REJECTED],
    )
    def test_get_non_approved_offer(self, client, validation):
        offer = offers_factories.OfferFactory(validation=validation)

        offer_id = offer.id
        with assert_num_queries(3):
            response = client.get(f"/native/v4/offer/{offer_id}")

        assert response.status_code == 404


class OfferHeaderV4Test:
    # 1. main SELECT (offer + joined mediations, product+productMediations, venue+address chain)
    # 2. stocks selectinload (needed for SEO metadata: min_price, hasStocks)
    base_num_queries = 2

    def test_get_offer_header_no_images(self, client):
        offer = offers_factories.OfferFactory()
        offers_factories.ThingStockFactory(offer=offer)

        offer_id = offer.id
        with assert_num_queries(self.base_num_queries):
            response = client.get(f"/native/v4/offer/{offer_id}/header")

        assert response.status_code == 200
        assert response.json["images"] is None
        assert response.json["likesCount"] == 0
        assert "metadata" in response.json

    def test_get_offer_header_with_mediation(self, client):
        offer = offers_factories.OfferFactory()
        offers_factories.ThingStockFactory(offer=offer)
        offers_factories.MediationFactory(offer=offer, thumbCount=1, credit="Photo credit")

        offer_id = offer.id
        with assert_num_queries(self.base_num_queries):
            response = client.get(f"/native/v4/offer/{offer_id}/header")

        assert response.status_code == 200
        images = response.json["images"]
        assert images is not None
        assert "recto" in images
        assert images["recto"]["credit"] == "Photo credit"

    def test_get_offer_header_with_product_mediations(self, client):
        product = offers_factories.ProductFactory(likesCount=42)
        offer = offers_factories.OfferFactory(product=product)
        offers_factories.ThingStockFactory(offer=offer)
        offers_factories.ProductMediationFactory(product=product, imageType=ImageType.RECTO)

        offer_id = offer.id
        with assert_num_queries(self.base_num_queries):
            response = client.get(f"/native/v4/offer/{offer_id}/header")

        assert response.status_code == 200
        assert response.json["likesCount"] == 42
        images = response.json["images"]
        assert images is not None
        assert "recto" in images

    def test_get_offer_header_metadata_name(self, client):
        offer = offers_factories.OfferFactory(name="Mon Super Spectacle")
        offers_factories.ThingStockFactory(offer=offer)

        offer_id = offer.id
        with assert_num_queries(self.base_num_queries):
            response = client.get(f"/native/v4/offer/{offer_id}/header")

        assert response.status_code == 200
        assert response.json["metadata"]["name"] == "Mon Super Spectacle"

    def test_get_offer_header_not_found(self, client):
        # 1. SELECT offer / 2. rollback / 3. rollback
        with assert_num_queries(3):
            response = client.get("/native/v4/offer/99999/header")

        assert response.status_code == 404


# ──────────────────────────────────────────────────────────────────────────────
# GET /native/v4/offer/<id>/offerer  —  venue + address + accessibility + desc
# ──────────────────────────────────────────────────────────────────────────────


class OfferOffererV4Test:
    # all joinedloads → single SQL query
    base_num_queries = 1

    def test_get_offer_offerer(self, client):
        offer = offers_factories.OfferFactory()

        offer_id = offer.id
        with assert_num_queries(self.base_num_queries):
            response = client.get(f"/native/v4/offer/{offer_id}/offerer")

        assert response.status_code == 200
        assert response.json["offererName"] == offer.venue.managingOfferer.name
        assert "venue" in response.json
        assert "address" in response.json
        assert "accessibility" in response.json

    def test_get_offer_offerer_address_from_venue(self, client):
        offer = offers_factories.OfferFactory()

        offer_id = offer.id
        with assert_num_queries(self.base_num_queries):
            response = client.get(f"/native/v4/offer/{offer_id}/offerer")

        assert response.status_code == 200
        address = response.json["address"]
        assert address is not None
        venue_addr = offer.venue.offererAddress.address
        assert address["city"] == venue_addr.city
        assert address["postalCode"] == venue_addr.postalCode

    def test_get_offer_offerer_description_from_product(self, client):
        product = offers_factories.ProductFactory(description="Description du produit")
        offer = offers_factories.OfferFactory(product=product)

        offer_id = offer.id
        with assert_num_queries(self.base_num_queries):
            response = client.get(f"/native/v4/offer/{offer_id}/offerer")

        assert response.status_code == 200
        assert response.json["description"] == "Description du produit"

    def test_get_offer_offerer_accessibility(self, client):
        offer = offers_factories.OfferFactory(
            audioDisabilityCompliant=True,
            mentalDisabilityCompliant=False,
            motorDisabilityCompliant=True,
            visualDisabilityCompliant=None,
        )

        offer_id = offer.id
        with assert_num_queries(self.base_num_queries):
            response = client.get(f"/native/v4/offer/{offer_id}/offerer")

        assert response.status_code == 200
        acc = response.json["accessibility"]
        assert acc["audioDisability"] is True
        assert acc["mentalDisability"] is False
        assert acc["motorDisability"] is True
        assert acc["visualDisability"] is None

    def test_get_offer_offerer_venue_info(self, client):
        offer = offers_factories.OfferFactory(venue__isPermanent=True)

        offer_id = offer.id
        with assert_num_queries(self.base_num_queries):
            response = client.get(f"/native/v4/offer/{offer_id}/offerer")

        assert response.status_code == 200
        venue = response.json["venue"]
        assert venue["id"] == offer.venue.id
        assert venue["isPermanent"] is True
        assert venue["name"] == offer.venue.name
        assert venue["publicName"] == offer.venue.publicName

    def test_get_offer_offerer_withdrawal_details(self, client):
        offer = offers_factories.OfferFactory(withdrawalDetails="Retrait en magasin le lundi")

        offer_id = offer.id
        with assert_num_queries(self.base_num_queries):
            response = client.get(f"/native/v4/offer/{offer_id}/offerer")

        assert response.status_code == 200
        assert response.json["withdrawalDetails"] == "Retrait en magasin le lundi"

    def test_get_offer_offerer_not_found(self, client):
        # 1. SELECT offer / 2. rollback / 3. rollback
        with assert_num_queries(3):
            response = client.get("/native/v4/offer/99999/offerer")

        assert response.status_code == 404


class OfferChroniclesV4Test:
    # query 1: resolve offer productId + chroniclesCount
    # query 2: paginated chronicles
    base_num_queries_with_product = 2
    # query 1: resolve, query 2: COUNT (no denormalized counter), query 3: paginated list
    base_num_queries_no_product = 3

    def test_get_chronicles_with_product(self, client):
        # Set chroniclesCount explicitly: the denormalized counter is not updated by factories
        product = offers_factories.ProductFactory(chroniclesCount=2)
        offer = offers_factories.OfferFactory(product=product)
        chronicle_1 = chronicles_factories.ChronicleFactory(
            products=[product],
            isActive=True,
            isSocialMediaDiffusible=True,
            isIdentityDiffusible=True,
            content="First chronicle content",
        )
        chronicles_factories.ChronicleFactory(
            products=[product],
            isActive=True,
            isSocialMediaDiffusible=True,
            isIdentityDiffusible=False,
            content="Second chronicle content",
        )
        # inactive: must not appear
        chronicles_factories.ChronicleFactory(products=[product], isActive=False, isSocialMediaDiffusible=True)

        offer_id = offer.id
        with assert_num_queries(self.base_num_queries_with_product):
            response = client.get(f"/native/v4/offer/{offer_id}/chronicles")

        assert response.status_code == 200
        assert response.json["chroniclesCount"] == 2  # from denormalized column
        chronicles = response.json["chronicles"]
        assert len(chronicles) == 2
        # ordered by id desc → most recent first
        assert chronicles[0]["content"] == "Second chronicle content"
        assert chronicles[0]["author"] is None  # isIdentityDiffusible=False
        assert chronicles[1]["content"] == "First chronicle content"
        assert chronicles[1]["author"]["firstName"] == chronicle_1.firstName

    def test_get_chronicles_without_product(self, client):
        # Event offer with no product → no denormalized counter, uses COUNT query
        offer = offers_factories.EventOfferFactory()
        offers_factories.EventStockFactory(offer=offer)
        chronicles_factories.ChronicleFactory(
            offers=[offer],
            isActive=True,
            isSocialMediaDiffusible=True,
            content="Event chronicle content",
        )

        offer_id = offer.id
        with assert_num_queries(self.base_num_queries_no_product):
            response = client.get(f"/native/v4/offer/{offer_id}/chronicles")

        assert response.status_code == 200
        assert response.json["chroniclesCount"] == 1
        assert len(response.json["chronicles"]) == 1
        assert response.json["chronicles"][0]["content"] == "Event chronicle content"

    def test_get_chronicles_pagination(self, client):
        product = offers_factories.ProductFactory(chroniclesCount=3)
        offer = offers_factories.OfferFactory(product=product)
        chronicles_factories.ChronicleFactory.create_batch(
            3, products=[product], isActive=True, isSocialMediaDiffusible=True
        )

        offer_id = offer.id
        with assert_num_queries(self.base_num_queries_with_product):
            response = client.get(f"/native/v4/offer/{offer_id}/chronicles?page=1&limit=2")

        assert response.status_code == 200
        assert response.json["chroniclesCount"] == 3
        assert len(response.json["chronicles"]) == 2

    def test_get_chronicles_full_content_not_truncated(self, client):
        long_content = ("mot " * 100).rstrip()  # ~400 chars, well above the 255 preview limit
        product = offers_factories.ProductFactory(chroniclesCount=1)
        offer = offers_factories.OfferFactory(product=product)
        chronicles_factories.ChronicleFactory(
            products=[product], isActive=True, isSocialMediaDiffusible=True, content=long_content
        )

        offer_id = offer.id
        with assert_num_queries(self.base_num_queries_with_product):
            response = client.get(f"/native/v4/offer/{offer_id}/chronicles")

        assert response.status_code == 200
        assert response.json["chronicles"][0]["content"] == long_content

    def test_get_chronicles_not_found(self, client):
        # 1 resolve query returns None → ResourceNotFoundError + rollbacks
        response = client.get("/native/v4/offer/99999/chronicles")
        assert response.status_code == 404


class OfferProAdvicesV4Test:
    # query 1: resolve productId + proAdvicesCount
    # query 2: get_pro_advices
    base_num_queries = 2

    def test_get_pro_advices_with_product(self, client):
        product = offers_factories.ProductFactory(proAdvicesCount=1)
        offer = offers_factories.OfferFactory(product=product)
        pro_advice = offers_factories.ProAdviceFactory(offer=offer)

        offer_id = offer.id
        with assert_num_queries(self.base_num_queries):
            response = client.get(f"/native/v4/offer/{offer_id}/pro_advices")

        assert response.status_code == 200
        assert response.json["proAdvicesCount"] == 1
        advices = response.json["proAdvices"]
        assert len(advices) == 1
        assert advices[0]["content"] == pro_advice.content
        assert advices[0]["venueId"] == offer.venue.id
        assert advices[0]["venueName"] == offer.venue.publicName
        assert advices[0]["publicationDatetime"] == date_utils.format_into_utc_date(pro_advice.updatedAt)

    def test_get_pro_advices_without_product(self, client):
        offer = offers_factories.OfferFactory()
        offers_factories.ProAdviceFactory(offer=offer)

        offer_id = offer.id
        with assert_num_queries(self.base_num_queries):
            response = client.get(f"/native/v4/offer/{offer_id}/pro_advices")

        assert response.status_code == 200
        # no product → total from offset + len(results)
        assert response.json["proAdvicesCount"] == 1
        assert len(response.json["proAdvices"]) == 1

    def test_get_pro_advices_author_can_be_null(self, client):
        offer = offers_factories.OfferFactory()
        offers_factories.ProAdviceFactory(offer=offer, author=None)

        offer_id = offer.id
        with assert_num_queries(self.base_num_queries):
            response = client.get(f"/native/v4/offer/{offer_id}/pro_advices")

        assert response.status_code == 200
        assert response.json["proAdvices"][0]["author"] is None

    def test_get_pro_advices_not_found(self, client):
        response = client.get("/native/v4/offer/99999/pro_advices")
        assert response.status_code == 404


class OfferStocksV4Test:
    # 1. SELECT offer existence + COUNT active stocks
    # 2. SELECT paginated stocks (+ joinedload priceCategory, priceCategoryLabel, offer.url)
    base_num_queries = 2

    def test_get_stocks_thing_offer(self, client):
        offer = offers_factories.OfferFactory()
        stock = offers_factories.ThingStockFactory(offer=offer, price=12.34)

        offer_id = offer.id
        with assert_num_queries(self.base_num_queries):
            response = client.get(f"/native/v4/offer/{offer_id}/stocks")

        assert response.status_code == 200
        assert response.json["stocksCount"] == 1
        assert len(response.json["stocks"]) == 1
        assert response.json["stocks"][0]["id"] == stock.id
        assert response.json["stocks"][0]["price"] == 1234

    def test_get_stocks_event_offer_with_price_category(self, client):
        offer = offers_factories.EventOfferFactory(subcategoryId=subcategories.SEANCE_CINE.id)
        stock = offers_factories.EventStockFactory(
            offer=offer, price=9.99, quantity=100, priceCategory__label="Tarif plein"
        )

        offer_id = offer.id
        with assert_num_queries(self.base_num_queries):
            response = client.get(f"/native/v4/offer/{offer_id}/stocks")

        assert response.status_code == 200
        assert response.json["stocksCount"] == 1
        assert response.json["stocks"][0]["id"] == stock.id
        assert response.json["stocks"][0]["priceCategoryLabel"] == "Tarif plein"
        assert response.json["stocks"][0]["beginningDatetime"] is not None

    def test_get_stocks_excludes_soft_deleted(self, client):
        offer = offers_factories.OfferFactory()
        offers_factories.ThingStockFactory(offer=offer, isSoftDeleted=True)
        active = offers_factories.ThingStockFactory(offer=offer)

        offer_id = offer.id
        with assert_num_queries(self.base_num_queries):
            response = client.get(f"/native/v4/offer/{offer_id}/stocks")

        assert response.status_code == 200
        assert response.json["stocksCount"] == 1
        assert response.json["stocks"][0]["id"] == active.id

    def test_get_stocks_pagination(self, client):
        offer = offers_factories.OfferFactory()
        stocks = [offers_factories.ThingStockFactory(offer=offer) for _ in range(5)]

        offer_id = offer.id
        with assert_num_queries(self.base_num_queries):
            response = client.get(f"/native/v4/offer/{offer_id}/stocks?page=2&limit=2")

        assert response.status_code == 200
        assert response.json["stocksCount"] == 5
        assert len(response.json["stocks"]) == 2
        returned_ids = {s["id"] for s in response.json["stocks"]}
        assert returned_ids == {stocks[2].id, stocks[3].id}

    def test_get_stocks_not_found(self, client):
        response = client.get("/native/v4/offer/99999/stocks")
        assert response.status_code == 404
