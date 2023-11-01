import random

from factory.faker import faker

from pcapi.core.categories import subcategories_v2
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offers import factories as offers_factories
from pcapi.core.providers.titelive_gtl import GTLS
from pcapi.sandboxes.scripts.creators.test_cases.venues_mock import venues


Fake = faker.Faker(locale="fr_FR")


def save_test_cases_sandbox() -> None:
    create_offers_with_gtls()
    create_offers_with_same_ean()


def create_offers_with_gtls() -> None:
    librairie_gtl = offerers_factories.VenueFactory(
        name="Librairie des GTls",
        venueTypeCode=offerers_models.VenueTypeCode.BOOKSTORE,
        isPermanent=True,
        latitude=45.91967,
        longitude=3.06504,
        address="13 AVENUE BARADUC",
        postalCode="63140",
        city="CHATEL-GUYON",
        departementCode="63",
    )
    create_offers_for_each_gtl_level_1(10, librairie_gtl)
    create_offers_with_gtl_id("01030000", 10, librairie_gtl)  # littérature, Œuvres classiques
    create_offers_with_gtl_id("01030100", 10, librairie_gtl)  # littérature, Œuvres classiques, Antiquité
    create_offers_with_gtl_id(
        "01030102", 10, librairie_gtl
    )  # littérature, Œuvres classiques, Antiquité, Littérature grecque antique

    # un librairie que pour des mangas

    librairie_manga = offerers_factories.VenueFactory(
        name="Librairie des mangas",
        venueTypeCode=offerers_models.VenueTypeCode.BOOKSTORE,
        isPermanent=True,
        latitude=46.66979,
        longitude=-1.42979,
        address="11 RUE GEORGES CLEMENCEAU",
        postalCode="85000",
        city="LA ROCHE-SUR-YON",
        departementCode="85",
    )
    create_offers_with_gtl_id("03050300)", 10, librairie_manga)  # 10 mangas


def create_offers_for_each_gtl_level_1(size_per_gtl_level_1: int, venue: offerers_models.Venue) -> None:
    for gtl_id_prefix in range(1, 14):
        gtl_id_prefix_str = str(gtl_id_prefix).zfill(2)
        gtl_ids = list(
            filter(
                # pylint: disable=cell-var-from-loop
                lambda gtl_id: gtl_id.startswith(
                    gtl_id_prefix_str
                ),  # gtl_id_prefix_str changes at each iteration, we tested that lambda considers the last value so it's fine to disable the warning
                GTLS.keys(),
            )
        )
        for _ in range(size_per_gtl_level_1):
            gtl_id = random.choice(gtl_ids)
            create_offers_with_gtl_id(gtl_id, 1, venue)


def create_offers_with_gtl_id(gtl_id: str, size_per_gtl: int, venue: offerers_models.Venue) -> None:
    product = offers_factories.ProductFactory(
        subcategoryId=subcategories_v2.LIVRE_PAPIER.id,
        extraData={"gtl_id": gtl_id, "author": Fake.name()},
    )
    offers = offers_factories.OfferFactory.create_batch(
        product=product,
        size=size_per_gtl,
        isActive=True,
        venue=venue,
        extraData={"gtl_id": gtl_id, "author": Fake.name()},
    )
    for offer in offers:
        offers_factories.StockFactory.create_batch(
            size=random.randint(1, 10),
            offer=offer,
        )


def create_offers_with_same_ean() -> None:
    offers = []
    ean = Fake.ean13()
    author = Fake.name()
    product = offers_factories.ProductFactory(
        name="Le livre du pass Culture",
        subcategoryId=subcategories_v2.LIVRE_PAPIER.id,
        extraData={
            "ean": ean,
            "author": author,
        },
    )
    for venue_data in venues:
        offers.append(
            offers_factories.OfferFactory(
                product=product,
                isActive=True,
                subcategoryId=subcategories_v2.LIVRE_PAPIER.id,
                venue=offerers_factories.VenueFactory(
                    name=venue_data["name"],
                    venueTypeCode=offerers_models.VenueTypeCode.BOOKSTORE,
                    isPermanent=True,
                    latitude=venue_data["latitude"],
                    longitude=venue_data["longitude"],
                    address=venue_data["address"],
                    postalCode=venue_data["postalCode"],
                    city=venue_data["city"],
                    departementCode=venue_data["departementCode"],
                ),
                extraData={
                    "ean": ean,
                    "author": author,
                },
            )
        )
        for offer in offers:
            offers_factories.StockFactory.create_batch(
                size=random.randint(1, 10),
                offer=offer,
            )
    for _ in range(10):
        ean = Fake.ean13()
        author = Fake.name()
        create_offer_with_ean(ean, random.choice(offers).venue, author=author)


def create_offer_with_ean(ean: str, venue: offerers_models.Venue, author: str) -> None:
    product = offers_factories.ProductFactory(
        subcategoryId=subcategories_v2.LIVRE_PAPIER.id,
        extraData={"ean": ean, "author": author},
    )
    offer = offers_factories.OfferFactory(
        isActive=True,
        product=product,
        extraData={"ean": ean, "author": author},
        venue=venue,
    )
    offers_factories.StockFactory.create_batch(
        size=random.randint(1, 10),
        offer=offer,
    )
