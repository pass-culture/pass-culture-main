import datetime
import itertools
import pathlib
import typing

import pcapi.sandboxes.thumbs.generic_pictures as generic_picture_thumbs
from pcapi.connectors import thumb_storage
from pcapi.core.bookings import factories as bookings_factories
from pcapi.core.categories import subcategories
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offers import factories as offers_factories
from pcapi.core.offers import models as offers_models
from pcapi.core.offers.models import ImageType
from pcapi.core.providers import factories as providers_factories
from pcapi.sandboxes.scripts.creators.test_cases import venues_mock
from pcapi.sandboxes.scripts.utils.helpers import log_func_duration


@log_func_duration
def create_cinema_data() -> None:
    venues = _create_allocine_venues()
    products = create_movie_products()
    create_offer_and_stocks_for_cinemas(venues, products)
    create_enriched_screenings_for_movie_page(venues)
    create_enriched_screenings_for_cinema_page(venues[0].managingOfferer, products)


def create_offer_and_stocks_for_cinemas(
    venues: list[offerers_models.Venue], products: list["offers_models.Product"]
) -> None:
    for venue in venues:
        for idx, product in enumerate(products):
            movie_offer = offers_factories.OfferFactory(product=product, venue=venue)
            stocks = []
            for daydelta in (0, 20, 4):
                day = datetime.date.today() + datetime.timedelta(days=daydelta)
                for hour in (11, 17, 21):
                    beginning_datetime = datetime.datetime.combine(day, datetime.time(hour=hour))
                    quantity = daydelta * hour + 1
                    stock = offers_factories.StockFactory(
                        offer=movie_offer, beginningDatetime=beginning_datetime, quantity=quantity
                    )
                    stocks.append(stock)

            product_bookings = idx + 1
            # We want the two most popular products to have the same number of bookings
            # to test movie sorting based on other criterias
            if product == products[-1]:
                product_bookings -= 1

            for stock_idx in range(product_bookings):
                bookings_factories.BookingFactory(stock=stocks[stock_idx % len(stocks)])


def _extract_values(data: typing.Any) -> typing.Generator[str]:
    if isinstance(data, dict):
        for val in data.values():
            yield from _extract_values(val)
    elif isinstance(data, list):
        for item in data:
            yield from _extract_values(item)
    elif data is not None:
        yield data


_without_audio_nor_special_event = {
    "language": "VF",
    "audio": "DOLBY_ATMOS",
    "video": None,
    "accessibility": {"audio": [], "mental": [], "motor": ["PMR"], "visual": ["GRETA"]},
    "specialEventType": None,
}
_without_video_nor_special_event = {
    "language": "VF",
    "audio": "DOLBY_ATMOS",
    "video": None,
    "accessibility": {"audio": ["CCAP"], "mental": ["RELAX"], "motor": [], "visual": ["GRETA"]},
    "specialEventType": None,
}
_without_special_event = {
    "language": "VF",
    "audio": "DOLBY_ATMOS",
    "video": "SCREEN_X",
    "accessibility": {"audio": ["CCAP"], "mental": ["RELAX"], "motor": ["PMR"], "visual": []},
    "specialEventType": None,
}
_without_accessibility_features = {
    "language": "VF",
    "audio": "DOLBY_ATMOS",
    "video": "SCREEN_X",
    "accessibility": {"audio": [], "mental": [], "motor": [], "visual": []},
    "specialEventType": "AVANT_PREMIERE",
}
_all_features = {
    "language": "VF",
    "audio": "DOLBY_ATMOS",
    "video": "SCREEN_X",
    "accessibility": {"audio": ["CCAP"], "mental": ["RELAX"], "motor": ["PMR"], "visual": ["GRETA"]},
    "specialEventType": "AVANT_PREMIERE",
}


def create_enriched_screenings_for_movie_page(venues: list[offerers_models.Venue]) -> None:
    assert len(venues) > 2
    product = offers_factories.ProductFactory.create(
        subcategoryId=subcategories.SEANCE_CINE.id,
        description="Film avec projections 3D/IMAX/Avant-première/etc.",
        name="Film avec séances enrichies",
        extraData={"allocineId": 123456},
        durationMinutes=90,
    )
    image_paths = itertools.cycle(pathlib.Path(generic_picture_thumbs.__path__[0]).iterdir())
    mediation = offers_factories.ProductMediationFactory.create(product=product, imageType=ImageType.POSTER)
    thumb_storage.create_thumb(product, next(image_paths).read_bytes(), keep_ratio=True, object_id=mediation.uuid)

    in_7_days = datetime.date.today() + datetime.timedelta(days=7)
    venue_without_features = venues[0]
    offer_without_features = offers_factories.OfferFactory(product=product, venue=venue_without_features)
    # 5 stocks is a minimum to able horizontal scrolling on mobile screens
    for hour, minute in ((5, 0), (11, 15), (14, 30), (18, 30), (21, 45)):
        offers_factories.StockFactory(
            offer=offer_without_features,
            features=[],
            price=5,
            beginningDatetime=datetime.datetime.combine(in_7_days, datetime.time(hour=hour, minute=minute)),
        )

    venue_with_all_features = venues[1]
    offer_with_all_features = offers_factories.OfferFactory(product=product, venue=venue_with_all_features)
    all_features = list(_extract_values(_all_features))
    for hour, minute in ((5, 0), (11, 15), (14, 30), (18, 30), (21, 45)):
        offers_factories.StockFactory(
            offer=offer_with_all_features,
            features=all_features,
            price=20.99,
            beginningDatetime=datetime.datetime.combine(in_7_days, datetime.time(hour=hour, minute=minute)),
        )

    venue_with_mixed_features = venues[2]
    offer_with_mixed_features = offers_factories.OfferFactory(product=product, venue=venue_with_mixed_features)
    for (features, price), (hour, minute) in zip(
        (
            (_without_audio_nor_special_event, 15),
            (_without_video_nor_special_event, 12.50),
            (_without_special_event, 17.80),
            (_without_accessibility_features, 19.10),
            (_all_features, 20.99),
        ),
        ((5, 0), (11, 15), (14, 30), (18, 30), (21, 45)),
    ):
        offers_factories.StockFactory(
            offer=offer_with_mixed_features,
            features=list(_extract_values(features)),
            price=price,
            beginningDatetime=datetime.datetime.combine(in_7_days, datetime.time(hour=hour, minute=minute)),
        )


def create_enriched_screenings_for_cinema_page(
    offerer: offerers_models.Offerer, products: list["offers_models.Product"]
) -> None:
    assert len(products) > 2
    venue = offerers_factories.VenueFactory.create(
        name="Cinéma avec séances enrichies - Paris",
        activity=offerers_models.Activity.CINEMA,
        venueTypeCode=offerers_models.VenueTypeCode.MOVIE,
        offererAddress__address__latitude=48.858,
        offererAddress__address__longitude=2.347,
        offererAddress__address__street="2 rue Saint-Denis",
        offererAddress__address__postalCode="75001",
        offererAddress__address__city="Paris",
        offererAddress__address__departmentCode="75",
        managingOfferer=offerer,
    )

    in_7_days = datetime.date.today() + datetime.timedelta(days=7)
    movie_without_features = products[0]
    offer_without_features = offers_factories.OfferFactory(product=movie_without_features, venue=venue)
    # 5 stocks is a minimum to able horizontal scrolling on mobile screens
    for hour, minute in ((5, 0), (11, 15), (14, 30), (18, 30), (21, 45)):
        offers_factories.StockFactory(
            offer=offer_without_features,
            features=[],
            price=5,
            beginningDatetime=datetime.datetime.combine(in_7_days, datetime.time(hour=hour, minute=minute)),
        )

    movie_with_all_features = products[1]
    offer_with_all_features = offers_factories.OfferFactory(product=movie_with_all_features, venue=venue)
    all_features = list(_extract_values(_all_features))
    for hour, minute in ((5, 0), (11, 15), (14, 30), (18, 30), (21, 45)):
        offers_factories.StockFactory(
            offer=offer_with_all_features,
            features=all_features,
            price=20.99,
            beginningDatetime=datetime.datetime.combine(in_7_days, datetime.time(hour=hour, minute=minute)),
        )

    movie_with_mixed_features = products[2]
    offer_with_mixed_features = offers_factories.OfferFactory(product=movie_with_mixed_features, venue=venue)
    for (features, price), (hour, minute) in zip(
        (
            (_without_audio_nor_special_event, 15),
            (_without_video_nor_special_event, 12.50),
            (_without_special_event, 17.80),
            (_without_accessibility_features, 19.10),
            (_all_features, 20.99),
        ),
        ((5, 0), (11, 15), (14, 30), (18, 30), (21, 45)),
    ):
        offers_factories.StockFactory(
            offer=offer_with_mixed_features,
            features=list(_extract_values(features)),
            price=price,
            beginningDatetime=datetime.datetime.combine(in_7_days, datetime.time(hour=hour, minute=minute)),
        )


def create_movie_products(offset: int = 0) -> list["offers_models.Product"]:
    image_paths = itertools.cycle(pathlib.Path(generic_picture_thumbs.__path__[0]).iterdir())
    products = []
    for i in range(1 + offset, 4 + offset):
        product = offers_factories.ProductFactory.create(
            subcategoryId=subcategories.SEANCE_CINE.id,
            description=f"Description du film {i}",
            name=f"Film {i}",
            extraData={"allocineId": 100_000 + i},
            durationMinutes=115 + i,
        )
        mediation = offers_factories.ProductMediationFactory.create(product=product, imageType=ImageType.POSTER)
        thumb_storage.create_thumb(product, next(image_paths).read_bytes(), keep_ratio=True, object_id=mediation.uuid)
        products.append(product)

    return products


def _create_allocine_venues() -> list[offerers_models.Venue]:
    venues = []
    for venue_data in venues_mock.cinemas_venues:
        allocine_offerer = offerers_factories.OffererFactory.create(
            name=f"Structure du lieu allocine {venue_data['name']}"
        )
        offerers_factories.UserOffererFactory.create(offerer=allocine_offerer, user__email="api@example.com")
        allocine_synchonized_venue = offerers_factories.VenueFactory.create(
            name=venue_data["name"],
            venueTypeCode=offerers_models.VenueTypeCode.MOVIE,
            offererAddress__address__latitude=venue_data["latitude"],
            offererAddress__address__longitude=venue_data["longitude"],
            offererAddress__address__street=venue_data["address"],
            offererAddress__address__postalCode=venue_data["postalCode"],
            offererAddress__address__city=venue_data["city"],
            offererAddress__address__departmentCode=venue_data["departementCode"],
            offererAddress__address__banId=venue_data["banId"],
            managingOfferer=allocine_offerer,
        )
        allocine_provider = providers_factories.AllocineProviderFactory.create(isActive=True)
        theater = providers_factories.AllocineTheaterFactory.create(
            siret=allocine_synchonized_venue.siret,
            theaterId=venue_data["theaterId"],
            internalId=venue_data["internalId"],
        )
        pivot = providers_factories.AllocinePivotFactory.create(
            venue=allocine_synchonized_venue, theaterId=theater.theaterId, internalId=theater.internalId
        )
        providers_factories.AllocineVenueProviderFactory.create(
            internalId=theater.internalId,
            provider=allocine_provider,
            venue=allocine_synchonized_venue,
            venueIdAtOfferProvider=pivot.theaterId,
        )
        venues.append(allocine_synchonized_venue)

    return venues
