import datetime
import random

from factory.faker import faker

from pcapi.core.categories import subcategories_v2
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offers import factories as offers_factories
from pcapi.core.providers import factories as providers_factory
from pcapi.core.providers.titelive_gtl import GTLS
from pcapi.sandboxes.scripts.creators.test_cases import venues_mock


Fake = faker.Faker(locale="fr_FR")


def save_test_cases_sandbox() -> None:
    create_offers_with_gtls()
    create_offers_with_same_ean()
    create_venues_across_cities()
    create_offers_for_each_subcategory()
    create_offers_with_same_author()


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
        gtl_ids = [gtl_id for gtl_id in GTLS if gtl_id.startswith(gtl_id_prefix_str)]

        for _ in range(size_per_gtl_level_1):
            gtl_id = random.choice(gtl_ids)
            create_offers_with_gtl_id(gtl_id, 1, venue)


def create_offers_with_gtl_id(gtl_id: str, size_per_gtl: int, venue: offerers_models.Venue) -> None:
    ean = Fake.ean13()
    product = offers_factories.ProductFactory(
        subcategoryId=subcategories_v2.LIVRE_PAPIER.id,
        lastProvider=providers_factory.PublicApiProviderFactory(name="BookProvider"),
        idAtProviders=ean,
        extraData={"gtl_id": gtl_id, "author": Fake.name(), "ean": ean},
    )
    offers = offers_factories.OfferFactory.create_batch(
        product=product,
        size=size_per_gtl,
        venue=venue,
        extraData={"gtl_id": gtl_id, "author": Fake.name(), "ean": ean},
    )
    for offer in offers:
        offers_factories.StockFactory(
            offer=offer,
        )


def create_offers_with_same_ean() -> None:
    offers = []
    ean = Fake.ean13()
    author = Fake.name()
    product = offers_factories.ProductFactory(
        name="Le livre du pass Culture",
        subcategoryId=subcategories_v2.LIVRE_PAPIER.id,
        lastProvider=providers_factory.PublicApiProviderFactory(name="BookProvider"),
        idAtProviders=ean,
        extraData={
            "ean": ean,
            "author": author,
        },
    )
    for venue_data in venues_mock.venues:
        offers.append(
            offers_factories.OfferFactory(
                product=product,
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
            offers_factories.StockFactory(quantity=random.randint(10, 100), offer=offer)
    for _ in range(10):
        ean = Fake.ean13()
        author = Fake.name()
        create_offer_with_ean(ean, random.choice(offers).venue, author=author)


def create_offer_with_ean(ean: str, venue: offerers_models.Venue, author: str) -> None:
    product = offers_factories.ProductFactory(
        subcategoryId=subcategories_v2.LIVRE_PAPIER.id,
        lastProvider=providers_factory.PublicApiProviderFactory(name="BookProvider"),
        idAtProviders=ean,
        extraData={"ean": ean, "author": author},
    )
    offer = offers_factories.OfferFactory(
        product=product,
        extraData={"ean": ean, "author": author},
        venue=venue,
    )
    offers_factories.StockFactory(quantity=random.randint(10, 100), offer=offer)


def create_venues_across_cities() -> None:
    venues_by_city = [venues_mock.paris_venues, venues_mock.lyon_venues, venues_mock.mayotte_venues]
    for venues_list in venues_by_city:
        for venue, venue_type_code in zip(venues_list, offerers_models.VenueTypeCode):
            venue = offerers_factories.VenueFactory(
                name=venue["city"] + "-" + venue["name"],
                venueTypeCode=venue_type_code,
                isPermanent=True,
                latitude=venue["latitude"],
                longitude=venue["longitude"],
                address=venue["address"],
                postalCode=venue["postalCode"],
                city=venue["city"],
                departementCode=venue["departementCode"],
            )
            for _ in range(7):
                offer = offers_factories.OfferFactory(
                    venue=venue,
                    product=None,
                    subcategoryId=random.choice(subcategories_v2.ALL_SUBCATEGORIES).id,
                    name=Fake.sentence(nb_words=3, variable_nb_words=True)[:-1],
                    description=Fake.paragraph(nb_sentences=5, variable_nb_sentences=True),
                    url=None,
                )
                for _ in range(random.randint(1, 10)):
                    offers_factories.StockFactory(quantity=random.randint(10, 100), offer=offer)

            for _ in range(3):
                offers_factories.EventOfferFactory(
                    venue=venue,
                    product=None,
                    subcategoryId=random.choice(list(subcategories_v2.EVENT_SUBCATEGORIES)),
                    name=Fake.sentence(nb_words=3, variable_nb_words=True)[:-1],
                    description=Fake.paragraph(nb_sentences=5, variable_nb_sentences=True),
                    url=None,
                )
                for _ in range(random.randint(1, 10)):
                    offers_factories.EventStockFactory(
                        quantity=random.randint(10, 100),
                        offer=offer,
                        beginningDatetime=datetime.datetime.utcnow()
                        + datetime.timedelta(
                            days=random.randint(30, 59),
                            hours=random.randint(1, 23),
                            minutes=random.randint(1, 59),
                            seconds=random.randint(1, 59),
                        ),
                    )


def create_offers_for_each_subcategory() -> None:
    for subcategory in subcategories_v2.ALL_SUBCATEGORIES:
        if subcategory.id in subcategories_v2.EVENT_SUBCATEGORIES:
            offers_factories.EventStockFactory.create_batch(
                size=10,
                offer__product=None,
                offer__subcategoryId=subcategory.id,
                quantity=random.randint(10, 100),
                beginningDatetime=datetime.datetime.utcnow()
                + datetime.timedelta(
                    days=random.randint(30, 59),
                    hours=random.randint(1, 23),
                    minutes=random.randint(1, 59),
                    seconds=random.randint(1, 59),
                ),
            )
        else:
            offers_factories.StockFactory.create_batch(
                size=10,
                offer__product=None,
                offer__subcategoryId=subcategory.id,
                quantity=random.randint(10, 100),
            )


def create_offers_with_same_author() -> None:
    venues = [
        offerers_factories.VenueFactory(
            name="same author " + str(venue["name"]),
            venueTypeCode=offerers_models.VenueTypeCode.BOOKSTORE,
            isPermanent=True,
            latitude=venue["latitude"],
            longitude=venue["longitude"],
            address=venue["address"],
            postalCode=venue["postalCode"],
            city=venue["city"],
            departementCode=venue["departementCode"],
        )
        for venue in random.choices(venues_mock.venues, k=4)
    ]
    create_books_with_same_author(venues)
    create_single_book_author(venues)
    create_book_in_multiple_venues(venues)
    create_books_with_the_same_author_duplicated_in_multiple_venues(venues)
    create_multiauthors_books(venues)


def create_books_with_same_author(venues: list[offerers_models.Venue]) -> None:
    # an author with 16 different books
    author = Fake.name()
    for venue in venues:
        for _ in range(4):
            create_offer_with_ean(Fake.ean13(), venue, author=author)


def create_single_book_author(venues: list[offerers_models.Venue]) -> None:
    # an author with a single book in  a single venue
    author = Fake.name()
    create_offer_with_ean(Fake.ean13(), venues[0], author=author)


def create_book_in_multiple_venues(venues: list[offerers_models.Venue]) -> None:
    # an author with 1 book in multiple venues
    author = Fake.name()
    ean = Fake.ean13()
    product = offers_factories.ProductFactory(
        subcategoryId=subcategories_v2.LIVRE_PAPIER.id,
        extraData={"ean": ean, "author": author},
    )
    for venue in venues[:3]:
        offer = offers_factories.OfferFactory(
            product=product,
            extraData={"ean": ean, "author": author},
            venue=venue,
        )
        offers_factories.StockFactory(quantity=random.randint(10, 100), offer=offer)


def create_books_with_the_same_author_duplicated_in_multiple_venues(venues: list[offerers_models.Venue]) -> None:
    # an author with multiple books but some in all venues
    author = Fake.name()
    for tome in range(1, 11):
        ean = Fake.ean13()
        product = offers_factories.ProductFactory(
            name="One Piece tome " + str(tome),
            subcategoryId=subcategories_v2.LIVRE_PAPIER.id,
            extraData={"ean": ean, "author": author},
        )
        for venue in venues:
            offer = offers_factories.OfferFactory(
                product=product,
                extraData={"ean": ean, "author": author},
                venue=venue,
            )
            offers_factories.StockFactory(quantity=random.randint(10, 100), offer=offer)

    for tome in range(11, 16):
        ean = Fake.ean13()
        product = offers_factories.ProductFactory(
            name="One Piece tome " + str(tome),
            subcategoryId=subcategories_v2.LIVRE_PAPIER.id,
            extraData={"ean": ean, "author": author},
        )
        offer = offers_factories.OfferFactory(
            product=product,
            extraData={"ean": ean, "author": author},
            venue=venues[3],
        )
        offers_factories.StockFactory(quantity=random.randint(10, 100), offer=offer)


def create_multiauthors_books(venues: list[offerers_models.Venue]) -> None:
    # multiple authors
    authors = [Fake.name() for _ in range(4)]
    ean = Fake.ean13()
    product = offers_factories.ProductFactory(
        name="multiauth",
        subcategoryId=subcategories_v2.LIVRE_PAPIER.id,
        extraData={"ean": ean, "author": ", ".join(authors)},
    )
    offer = offers_factories.OfferFactory(
        product=product,
        extraData={"ean": ean, "author": ", ".join(authors)},
        venue=venues[0],
    )
    offers_factories.StockFactory(quantity=random.randint(10, 100), offer=offer)

    for author in authors:
        for _ in range(4):
            create_offer_with_ean(Fake.ean13(), random.choice(venues), author=author)

    # author "collectif"
    author = "collectif"
    for _ in range(3):
        create_offer_with_ean(Fake.ean13(), random.choice(venues), author=author)
