import decimal

import pytest

import pcapi.core.offers.factories as offers_factories
from pcapi.scripts.stock import populate_event_stock_price_categories


@pytest.mark.usefixtures("db_session")
def test_populate_event_stock_price_categories():
    # Case 1 - An offer with a mix of stocks with price categories and without price categories
    ## 1a - Only one price
    event_1a = offers_factories.EventOfferFactory()
    price_category_1a = offers_factories.PriceCategoryFactory(
        offer=event_1a, price=11, priceCategoryLabel__label="Tarif 1"
    )
    stock_1a_first = offers_factories.EventStockFactory(
        offer=event_1a,
        priceCategory=price_category_1a,
        price=11,
    )
    stock_1a_second = offers_factories.EventStockFactory(
        offer=event_1a,
        priceCategory=None,
        price=11,
    )
    ## 1b - Multiple prices
    event_1b = offers_factories.EventOfferFactory()
    price_category_1b = offers_factories.PriceCategoryFactory(
        offer=event_1b, price=11, priceCategoryLabel__label="Tarif 1"
    )
    stock_1b_first = offers_factories.EventStockFactory(
        offer=event_1b,
        priceCategory=price_category_1b,
        price=11,
    )
    stock_1b_second = offers_factories.EventStockFactory(
        offer=event_1b,
        priceCategory=price_category_1b,
        price=11,
    )
    stock_1b_third = offers_factories.EventStockFactory(
        offer=event_1b,
        price=12.34,
        priceCategory=None,
    )

    # Case 2 - An offer with no price categories at all
    ## 2a - only one price
    event_2a = offers_factories.EventOfferFactory()
    stock_2a_first = offers_factories.EventStockFactory(
        offer=event_2a,
        price=12.34,
        priceCategory=None,
    )
    stock_2a_second = offers_factories.EventStockFactory(
        offer=event_2a,
        price=12.34,
        priceCategory=None,
    )
    ## 2b - multiple prices
    event_2b = offers_factories.EventOfferFactory()
    stock_2b_first = offers_factories.EventStockFactory(
        offer=event_2b,
        price=12.34,
        priceCategory=None,
    )
    stock_2b_second = offers_factories.EventStockFactory(
        offer=event_2b,
        price=12.34,
        priceCategory=None,
    )
    stock_2b_third = offers_factories.EventStockFactory(
        offer=event_2b,
        price=43.21,
        priceCategory=None,
    )

    # Case 3 - An offer with price categories on all stocks
    ## 3a - only one priceCategory
    event_3a = offers_factories.EventOfferFactory()
    price_category_3a = offers_factories.PriceCategoryFactory(
        offer=event_3a, price=12.34, priceCategoryLabel__label="Tarif 1"
    )
    stock_3a_first = offers_factories.EventStockFactory(
        offer=event_3a,
        price=12.34,
        priceCategory=price_category_3a,
    )
    stock_3a_second = offers_factories.EventStockFactory(
        offer=event_3a,
        price=12.34,
        priceCategory=price_category_3a,
    )

    ## 3b - multiples stocks
    event_3b = offers_factories.EventOfferFactory()
    price_category_3b_first = offers_factories.PriceCategoryFactory(
        offer=event_3b, price=12.34, priceCategoryLabel__label="Tarif 1"
    )
    price_category_3b_second = offers_factories.PriceCategoryFactory(
        offer=event_3b, price=43.21, priceCategoryLabel__label="Tarif 2"
    )
    stock_3b_first = offers_factories.EventStockFactory(
        offer=event_3b,
        price=12.34,
        priceCategory=price_category_3b_first,
    )
    stock_3b_second = offers_factories.EventStockFactory(
        offer=event_3b,
        price=12.34,
        priceCategory=price_category_3b_first,
    )
    stock_3b_third = offers_factories.EventStockFactory(
        offer=event_3b,
        price=43.21,
        priceCategory=price_category_3b_second,
    )

    populate_event_stock_price_categories.populate_event_stock_price_categories(creation_date=None)

    # case 1a
    price_categories_1a = sorted(event_1a.priceCategories, key=lambda d: d.price)
    assert len(price_categories_1a) == 1
    assert stock_1a_first.priceCategory == price_category_1a
    assert stock_1a_first.price == price_category_1a.price
    assert stock_1a_first.priceCategory.label == "Tarif unique"
    assert stock_1a_second.priceCategory == price_category_1a
    assert stock_1a_second.price == price_category_1a.price
    assert stock_1a_second.priceCategory.label == "Tarif unique"

    # case 1b
    price_categories_1b = sorted(event_1b.priceCategories, key=lambda d: d.price)
    assert len(price_categories_1b) == 2
    assert price_categories_1b[0].label == "Tarif 1"
    assert price_categories_1b[1].label == "Tarif 2"
    assert price_categories_1b[0].price == decimal.Decimal("11")
    assert price_categories_1b[1].price == decimal.Decimal("12.34")
    assert stock_1b_first.priceCategory == stock_1b_second.priceCategory == price_categories_1b[0]
    assert stock_1b_first.price == stock_1b_second.price == price_categories_1b[0].price
    assert stock_1b_third.priceCategory == price_categories_1b[1]
    assert stock_1b_third.price == price_categories_1b[1].price

    # case 2a
    [price_categories_2a] = event_2a.priceCategories
    assert price_categories_2a.label == "Tarif unique"
    assert price_categories_2a.price == decimal.Decimal("12.34")
    assert price_categories_2a == stock_2a_first.priceCategory == stock_2a_second.priceCategory
    assert stock_2a_first.price == stock_2a_second.price == price_categories_2a.price

    # case 2b
    price_categories_2b = sorted(event_2b.priceCategories, key=lambda d: d.price)
    assert len(price_categories_2b) == 2
    assert price_categories_2b[0].label == "Tarif 1"
    assert price_categories_2b[0].price == decimal.Decimal("12.34")
    assert price_categories_2b[1].label == "Tarif 2"
    assert price_categories_2b[1].price == decimal.Decimal("43.21")
    assert stock_2b_second.priceCategory == stock_2b_first.priceCategory == price_categories_2b[0]
    assert stock_2b_second.price == stock_2b_first.price == price_categories_2b[0].price
    assert stock_2b_third.priceCategory == price_categories_2b[1]
    assert stock_2b_third.price == price_categories_2b[1].price

    # case 3a
    [price_categories_3a] = event_3a.priceCategories
    assert price_categories_3a.label == "Tarif unique"
    assert price_categories_3a.price == decimal.Decimal("12.34")
    assert price_categories_3a == stock_3a_first.priceCategory == stock_3a_second.priceCategory
    assert stock_3a_first.price == stock_3a_second.price == price_categories_3a.price

    # case 3b
    price_categories_3b = sorted(event_3b.priceCategories, key=lambda d: d.price)
    assert len(price_categories_3b) == 2
    assert price_categories_3b[0].label == "Tarif 1"
    assert price_categories_3b[0].price == decimal.Decimal("12.34")
    assert price_categories_3b[1].label == "Tarif 2"
    assert price_categories_3b[1].price == decimal.Decimal("43.21")
    assert stock_3b_second.priceCategory == stock_3b_first.priceCategory == price_categories_3b[0]
    assert stock_3b_second.price == stock_3b_first.price == price_categories_3b[0].price
    assert stock_3b_third.priceCategory == price_categories_3b[1]
    assert stock_3b_third.price == price_categories_3b[1].price
