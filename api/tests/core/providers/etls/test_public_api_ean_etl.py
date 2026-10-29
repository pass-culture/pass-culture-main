import pytest

import pcapi.core.geography.factories as geography_factories
from pcapi.core.categories import subcategories
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offers import factories as offers_factories
from pcapi.core.offers import models as offers_models
from pcapi.core.offers import schemas as offers_schemas
from pcapi.core.providers import factories
from pcapi.core.providers.etls import public_api_ean_etl


@pytest.mark.usefixtures("db_session")
def test_extract_returns_existing_product():
    provider = factories.PublicApiProviderFactory()
    venue = offerers_factories.VenueFactory()
    event = offers_factories.ProductFactory(
        ean="2251745606264",
        gcuCompatibilityType=offers_models.GcuCompatibilityType.COMPATIBLE,
        subcategoryId=subcategories.SUPPORT_PHYSIQUE_MUSIQUE_CD.id,
    )
    product = offers_factories.ProductFactory(
        ean="2251745606265",
        gcuCompatibilityType=offers_models.GcuCompatibilityType.COMPATIBLE,
        subcategoryId=subcategories.CARTE_JEUNES.id,
    )
    offer = offers_factories.OfferFactory(subcategoryId=subcategories.CARTE_JEUNES.id, product=product, venue=venue)
    assert not offer.isEvent
    assert offer.ean == product.ean

    products_stocks = {}
    products_stocks[f"{event.ean}"] = offers_schemas.SerializedProductsStock(
        quantity=1,
        price=1,
        booking_limit_datetime=None,
        publication_datetime=None,
        booking_allowed_datetime=None,
        external_ticket_office_url=None,
    )
    products_stocks[f"{product.ean}"] = offers_schemas.SerializedProductsStock(
        quantity=1,
        price=1,
        booking_limit_datetime=None,
        publication_datetime=None,
        booking_allowed_datetime=None,
        external_ticket_office_url=None,
    )

    request_payload = offers_schemas.CreateOrUpdateEANOffersRequest(
        serialized_products_stocks=products_stocks,
        venue_id=venue.id,
        provider_id=provider.id,
        address_id=None,
        address_label=None,
    )

    result = public_api_ean_etl._extract(request_payload)

    assert result["venue"].id == venue.id
    assert result["provider"].id == provider.id
    assert result["offerer_address"].addressId == venue.offererAddress.addressId
    assert event.ean in result["products_by_ean"]
    assert product.ean not in result["products_by_ean"]
    assert offer.ean in result["offers_by_id_at_provider"]
    assert event.ean not in result["offers_by_id_at_provider"]
    assert result["offers_by_id_at_provider"][offer.ean].id == offer.id


@pytest.mark.usefixtures("db_session")
def test_extract_returns_existing_product_specific_cases():
    address = geography_factories.AddressFactory()
    provider = factories.PublicApiProviderFactory()
    venue = offerers_factories.VenueFactory()
    not_compatible_product = offers_factories.ProductFactory(
        ean="2251745606264",
        gcuCompatibilityType=offers_models.GcuCompatibilityType.PROVIDER_INCOMPATIBLE,
        subcategoryId=subcategories.SUPPORT_PHYSIQUE_MUSIQUE_CD.id,
    )

    wrong_sub_category_product = offers_factories.ProductFactory(
        ean="2251745606265",
        gcuCompatibilityType=offers_models.GcuCompatibilityType.COMPATIBLE,
        subcategoryId=subcategories.SEANCE_CINE.id,
    )

    not_existing_product_ean = "2251745606266"
    products_stocks = {}
    default_stock = offers_schemas.SerializedProductsStock(
        quantity=1,
        price=1,
        booking_limit_datetime=None,
        publication_datetime=None,
        booking_allowed_datetime=None,
        external_ticket_office_url=None,
    )
    products_stocks[not_existing_product_ean] = default_stock
    products_stocks[f"{wrong_sub_category_product.ean}"] = default_stock
    products_stocks[f"{not_compatible_product.ean}"] = default_stock

    request_payload = offers_schemas.CreateOrUpdateEANOffersRequest(
        serialized_products_stocks=products_stocks,
        venue_id=venue.id,
        provider_id=provider.id,
        address_id=address.id,
        address_label="Toto",
    )

    result = public_api_ean_etl._extract(request_payload)

    assert result["offerer_address"].addressId == address.id
    assert result["offerer_address"].label == "Toto"
    assert not_existing_product_ean not in result["products_by_ean"]
    assert wrong_sub_category_product not in result["products_by_ean"]
    assert not_compatible_product not in result["products_by_ean"]
