import datetime
import itertools
import pathlib
import random

from factory.faker import faker

from pcapi.core.bookings import factories as bookings_factories
from pcapi.core.categories import subcategories_v2
from pcapi.core.criteria import factories as criteria_factories
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offers import api as offers_api
from pcapi.core.offers import factories as offers_factories
from pcapi.core.offers.models import TiteliveImageType
from pcapi.core.providers import factories as providers_factories
from pcapi.core.providers.titelive_gtl import GTLS
from pcapi.core.users import factories as users_factories
from pcapi.repository import atomic
from pcapi.sandboxes.scripts.creators.industrial.create_industrial_gdpr_users import create_industrial_gdpr_users
from pcapi.sandboxes.scripts.creators.industrial.create_industrial_invoices import (
    create_specific_cashflow_batch_without_invoice,
)
from pcapi.sandboxes.scripts.creators.industrial.create_industrial_invoices import create_specific_invoice
from pcapi.sandboxes.scripts.creators.industrial.create_industrial_offer_price_limitation_rules import *
from pcapi.sandboxes.scripts.creators.industrial.create_industrial_offer_validation_rules import *
from pcapi.sandboxes.scripts.creators.industrial.create_industrial_offerer_with_custom_reimbursement_rule import (
    create_industrial_offerer_with_custom_reimbursement_rule,
)
from pcapi.sandboxes.scripts.creators.industrial.create_role_permissions import create_roles_with_permissions
from pcapi.sandboxes.scripts.creators.test_cases import venues_mock
from pcapi.sandboxes.scripts.utils.storage_utils import store_public_object_from_sandbox_assets
import pcapi.sandboxes.thumbs.generic_pictures as generic_picture_thumbs
from pcapi.scripts.venue.venue_label.create_venue_labels import create_venue_labels


Fake = faker.Faker(locale="fr_FR")


def save_test_cases_sandbox() -> None:
    create_offers_with_gtls()
    create_offers_with_same_ean()
    create_cinema_data()
    create_venues_across_cities()
    create_offers_for_each_subcategory()
    create_offers_with_same_author()
    create_roles_with_permissions()
    create_industrial_offer_price_limitation_rules()
    create_industrial_offer_validation_rules()
    create_industrial_gdpr_users()
    create_industrial_offerer_with_custom_reimbursement_rule()
    create_specific_invoice()
    create_specific_cashflow_batch_without_invoice()
    create_venue_labels(sandbox=True)
    create_venues_with_gmaps_image()
    create_app_beneficiary()
    create_venues_with_practical_info_graphical_edge_cases()
    create_institutional_website_offer_playlist()
    create_product_with_multiple_images()
    create_discord_users()


def create_offers_with_gtls() -> None:
    librairie_gtl = offerers_factories.VenueFactory(
        name="Librairie des GTls",
        venueTypeCode=offerers_models.VenueTypeCode.BOOKSTORE,
        latitude=45.91967,
        longitude=3.06504,
        street="13 AVENUE BARADUC",
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
        latitude=46.66979,
        longitude=-1.42979,
        street="11 RUE GEORGES CLEMENCEAU",
        postalCode="85000",
        city="LA ROCHE-SUR-YON",
        departementCode="85",
    )
    create_offers_with_gtl_id("03050300", 10, librairie_manga)  # 10 mangas


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
        lastProvider=providers_factories.PublicApiProviderFactory(name="BookProvider"),
        idAtProviders=ean,
        extraData={"gtl_id": gtl_id, "author": Fake.name(), "ean": ean},
    )
    offers = offers_factories.OfferFactory.create_batch(
        product=product,
        name=product.name,
        subcategoryId=product.subcategoryId,
        description=product.description,
        size=size_per_gtl,
        venue=venue,
    )
    for offer in offers:
        offers_factories.StockFactory(offer=offer)


def create_offers_with_same_ean() -> None:
    offers = []
    product = offers_factories.ProductFactory(
        name="Le livre du pass Culture",
        subcategoryId=subcategories_v2.LIVRE_PAPIER.id,
        lastProvider=providers_factories.PublicApiProviderFactory(name="BookProvider"),
    )
    for venue_data in venues_mock.venues:
        offers.append(
            offers_factories.OfferFactory(
                product=product,
                subcategoryId=subcategories_v2.LIVRE_PAPIER.id,
                venue=offerers_factories.VenueFactory(
                    name=venue_data["name"],
                    venueTypeCode=offerers_models.VenueTypeCode.BOOKSTORE,
                    latitude=venue_data["latitude"],
                    longitude=venue_data["longitude"],
                    street=venue_data["address"],
                    postalCode=venue_data["postalCode"],
                    city=venue_data["city"],
                    departementCode=venue_data["departementCode"],
                ),
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
        lastProvider=providers_factories.PublicApiProviderFactory(name="BookProvider"),
        idAtProviders=ean,
        extraData={"ean": ean, "author": author},
    )
    offer = offers_factories.OfferFactory(
        product=product,
        name=product.name,
        subcategoryId=product.subcategoryId,
        description=product.description,
        venue=venue,
    )
    offers_factories.StockFactory(quantity=random.randint(10, 100), offer=offer)


def _create_offer_and_stocks_for_allocine_venues(
    venues: list[offerers_models.Venue], products: list[offers_models.Product]
) -> None:
    for venue in venues:
        for idx, product in enumerate(products):
            movie_offer = offers_factories.OfferFactory(
                durationMinutes=product.durationMinutes,
                name=product.name,
                product=product,
                subcategoryId=subcategories_v2.SEANCE_CINE.id,
                venue=venue,
                extraData=product.extraData,
            )
            product_stocks = []
            for daydelta in range(30):
                day = datetime.date.today() + datetime.timedelta(days=daydelta)
                for hour in (0, 5, 11, 17, 21):
                    beginning_datetime = datetime.datetime.combine(day, datetime.time(hour=hour))
                    is_full = hour == 5
                    quantity = daydelta * hour + 1 if not is_full else 0
                    stock = offers_factories.StockFactory(
                        offer=movie_offer,
                        beginningDatetime=beginning_datetime,
                        bookingLimitDatetime=beginning_datetime - datetime.timedelta(minutes=30),
                        quantity=quantity,
                    )
                    if not is_full:
                        product_stocks.append(stock)

            product_bookings = idx + 1
            # We want the two most popular products to have the same number of bookings
            if product == products[-1]:
                product_bookings -= 1

            for stock_idx in range(product_bookings):
                bookings_factories.BookingFactory(stock=product_stocks[stock_idx % len(product_stocks)])


def create_cinema_data() -> None:
    venues = _create_allocine_venues()
    products = _create_movie_products()
    _create_offer_and_stocks_for_allocine_venues(venues, products)


def _create_movie_products() -> list[offers_models.Product]:
    return [
        offers_factories.ProductFactory(
            subcategoryId=subcategories_v2.SEANCE_CINE.id,
            description=f"Description du film {i}",
            name=f"Film {i}",
            extraData={"allocineId": 100_000 + i},
            durationMinutes=115 + i,
        )
        for i in range(1, 11)
    ]


def _create_allocine_venues() -> list[offerers_models.Venue]:
    venues = []
    for venue_data in venues_mock.cinemas_venues:
        allocine_offerer = offerers_factories.OffererFactory(name=f"Structure du lieu allocine {venue_data['name']}")
        offerers_factories.UserOffererFactory(offerer=allocine_offerer, user__email="api@example.com")
        allocine_synchonized_venue = offerers_factories.VenueFactory(
            name=venue_data["name"],
            venueTypeCode=offerers_models.VenueTypeCode.MOVIE,
            latitude=venue_data["latitude"],
            longitude=venue_data["longitude"],
            street=venue_data["address"],
            postalCode=venue_data["postalCode"],
            city=venue_data["city"],
            departementCode=venue_data["departementCode"],
            managingOfferer=allocine_offerer,
        )
        allocine_provider = providers_factories.AllocineProviderFactory(isActive=True)
        theater = providers_factories.AllocineTheaterFactory(
            siret=allocine_synchonized_venue.siret,
            theaterId=venue_data["theaterId"],
            internalId=venue_data["internalId"],
        )
        pivot = providers_factories.AllocinePivotFactory(
            venue=allocine_synchonized_venue, theaterId=theater.theaterId, internalId=theater.internalId
        )
        providers_factories.AllocineVenueProviderFactory(
            internalId=theater.internalId,
            provider=allocine_provider,
            venue=allocine_synchonized_venue,
            venueIdAtOfferProvider=pivot.theaterId,
        )
        venues.append(allocine_synchonized_venue)

    return venues


def create_venues_across_cities() -> None:
    venues_by_city = [venues_mock.paris_venues, venues_mock.lyon_venues, venues_mock.mayotte_venues]
    for venues_list in venues_by_city:
        for venue, venue_type_code in zip(venues_list, offerers_models.VenueTypeCode):
            venue = offerers_factories.VenueFactory(
                name=venue["city"] + "-" + venue["name"],
                venueTypeCode=venue_type_code,
                latitude=venue["latitude"],
                longitude=venue["longitude"],
                street=venue["address"],
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
        for i in range(1, 11):
            is_free = i % 2
            is_in_Paris = i < 6  # else it will be Marseille
            if subcategory.id in subcategories_v2.EVENT_SUBCATEGORIES:
                stock = offers_factories.EventStockFactory(
                    offer__product=None,
                    offer__subcategoryId=subcategory.id,
                    offer__venue__latitude=48.87004 if is_in_Paris else 43.29542,
                    offer__venue__longitude=2.37850 if is_in_Paris else 5.37421,
                    price=0 if is_free else i * 2,
                    quantity=i * 10,
                    beginningDatetime=datetime.datetime.utcnow()
                    + datetime.timedelta(
                        days=i + 7,
                        hours=(3 * i) % 60,
                        minutes=(5 * i) % 60,
                    ),
                )
            else:
                stock = offers_factories.StockFactory(
                    offer__product=None,
                    offer__subcategoryId=subcategory.id,
                    price=0 if is_free else 10,
                    quantity=i * 10,
                )
            mediation = offers_factories.MediationFactory(offer=stock.offer)
            store_public_object_from_sandbox_assets("thumbs", mediation, subcategory.id)


def create_offers_with_same_author() -> None:
    venues = [
        offerers_factories.VenueFactory(
            name="same author " + str(venue["name"]),
            venueTypeCode=offerers_models.VenueTypeCode.BOOKSTORE,
            latitude=venue["latitude"],
            longitude=venue["longitude"],
            street=venue["address"],
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
    product = offers_factories.ProductFactory(
        subcategoryId=subcategories_v2.LIVRE_PAPIER.id,
    )
    for venue in venues[:3]:
        offer = offers_factories.OfferFactory(
            product=product,
            name=product.name,
            description=product.description,
            subcategoryId=product.subcategoryId,
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
                name=product.name,
                subcategoryId=product.subcategoryId,
                description=product.description,
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
            name=product.name,
            subcategoryId=product.subcategoryId,
            description=product.description,
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
        name=product.name,
        subcategoryId=product.subcategoryId,
        description=product.description,
        venue=venues[0],
    )
    offers_factories.StockFactory(quantity=random.randint(10, 100), offer=offer)

    for author in authors:
        for _ in range(4):
            create_offer_with_ean(Fake.ean13(), random.choice(venues), author=author)

    author = "collectif"
    for _ in range(3):
        create_offer_with_ean(Fake.ean13(), random.choice(venues), author=author)


def create_venues_with_gmaps_image() -> None:
    venue_with_user_image_and_gmaps_image = offerers_factories.VenueFactory(
        isPermanent=True,
        name="venue_with_user_image_and_gmaps_image",
        _bannerUrl="https://storage.googleapis.com/passculture-metier-ehp-testing-assets-fine-grained/thumbs/offerers/FY",
    )
    offerers_factories.GooglePlacesInfoFactory(
        bannerUrl="https://storage.googleapis.com/passculture-metier-ehp-testing-assets-fine-grained/assets/Google_Maps_Logo_2020.png",
        venue=venue_with_user_image_and_gmaps_image,
        bannerMeta={"html_attributions": ['<a href="http://parhumans.wordpress.com">JC mc Crae</a>']},
    )

    venue_without_user_image_and_with_gmaps_image = offerers_factories.VenueFactory(
        isPermanent=True,
        name="venue_without_user_image_and_with_gmaps_image",
        _bannerUrl=None,
    )
    offerers_factories.GooglePlacesInfoFactory(
        bannerUrl="https://storage.googleapis.com/passculture-metier-ehp-testing-assets-fine-grained/assets/Google_Maps_Logo_2020.png",
        venue=venue_without_user_image_and_with_gmaps_image,
        bannerMeta={"html_attributions": ['<a href="http://python.com">Average python enjoyer</a>']},
    )
    venue_with_no_images = offerers_factories.VenueFactory(
        name="Lieu sans image",
        _bannerUrl=None,
        isPermanent=True,
    )
    offers_factories.StockFactory(
        offer=offers_factories.OfferFactory(
            venue=venue_with_user_image_and_gmaps_image,
            product=None,
            subcategoryId=random.choice(subcategories_v2.ALL_SUBCATEGORIES).id,
            name=Fake.sentence(nb_words=3, variable_nb_words=True)[:-1],
            description=Fake.paragraph(nb_sentences=5, variable_nb_sentences=True),
            url=None,
        )
    )
    offers_factories.StockFactory(
        offer=offers_factories.OfferFactory(
            venue=venue_without_user_image_and_with_gmaps_image,
            product=None,
            subcategoryId=random.choice(subcategories_v2.ALL_SUBCATEGORIES).id,
            name=Fake.sentence(nb_words=3, variable_nb_words=True)[:-1],
            description=Fake.paragraph(nb_sentences=5, variable_nb_sentences=True),
            url=None,
        )
    )
    offers_factories.StockFactory(
        offer=offers_factories.OfferFactory(
            venue=venue_with_no_images,
            product=None,
            subcategoryId=random.choice(subcategories_v2.ALL_SUBCATEGORIES).id,
            name=Fake.sentence(nb_words=3, variable_nb_words=True)[:-1],
            description=Fake.paragraph(nb_sentences=5, variable_nb_sentences=True),
            url=None,
        )
    )


def create_app_beneficiary() -> None:
    users_factories.BeneficiaryGrant18Factory(
        email="dev-tests-e2e@passculture.team",
        firstName=Fake.first_name(),
        lastName=Fake.last_name(),
        needsToFillCulturalSurvey=False,
    )


def create_venues_with_practical_info_graphical_edge_cases() -> None:
    offerers_factories.VenueFactory(
        name="Lieu avec un nom très long, qui atteint presque la limite de caractères en base de données et qui prend vraiment toute la place sur l'écran",
        isPermanent=True,
    )
    offerers_factories.VenueFactory(
        name="Lieu avec une adresse trop longue",
        street=(
            "50 rue de l'adresse la plus longue qui a presque atteint la limite de caractères en base de données, "
            "une adresse vraiment très longue qui prend toute la place sur l'écran, bâtiment B, étage 3, salle 4"
        ),
        isPermanent=True,
    )
    offerers_factories.VenueFactory(
        name="Lieu avec toutes les informations pratiques bien remplies",
        description=Fake.paragraph(nb_sentences=5, variable_nb_sentences=True),
        audioDisabilityCompliant=True,
        mentalDisabilityCompliant=False,
        motorDisabilityCompliant=False,
        visualDisabilityCompliant=True,
        withdrawalDetails="Venir récupérer l'offre sur place",
        isPermanent=True,
    )
    offerers_factories.VenueFactory(
        name="Lieu avec aucune information pratique",
        description=None,
        audioDisabilityCompliant=None,
        mentalDisabilityCompliant=None,
        motorDisabilityCompliant=None,
        visualDisabilityCompliant=None,
        contact=None,
        isPermanent=True,
    )
    offerers_factories.VenueFactory(
        name="Lieu avec aucun critère d’accessibilité rempli",
        audioDisabilityCompliant=None,
        mentalDisabilityCompliant=None,
        motorDisabilityCompliant=None,
        visualDisabilityCompliant=None,
        isPermanent=True,
    )
    offerers_factories.VenueFactory(
        name="Lieu avec tous les critères d’accessibilité remplis",
        audioDisabilityCompliant=True,
        mentalDisabilityCompliant=True,
        motorDisabilityCompliant=True,
        visualDisabilityCompliant=True,
        isPermanent=True,
    )
    offerers_factories.VenueFactory(
        name="Lieu avec seulement une description dans les informations pratiques",
        description=Fake.paragraph(nb_sentences=5, variable_nb_sentences=True),
        audioDisabilityCompliant=None,
        mentalDisabilityCompliant=None,
        motorDisabilityCompliant=None,
        visualDisabilityCompliant=None,
        contact=None,
        isPermanent=True,
    )
    offerers_factories.VenueFactory(
        name="Lieu qui a renseigné une adresse mail, un numéro de téléphone et un site web",
        isPermanent=True,
    )
    offerers_factories.VenueFactory(
        name="Lieu qui n’a renseigné aucun moyen de le contacter",
        contact=None,
        isPermanent=True,
    )
    offerers_factories.VenueFactory(
        name="Lieu avec seulement les modalités de retrait dans les informations pratiques",
        audioDisabilityCompliant=None,
        mentalDisabilityCompliant=None,
        motorDisabilityCompliant=None,
        visualDisabilityCompliant=None,
        contact=None,
        description=None,
        withdrawalDetails="Venir récupérer l'offre sur place",
        isPermanent=True,
    )
    partial_contact_venue = offerers_factories.VenueFactory(
        name="Lieu qui a renseigné seulement un site internet",
        description=None,
        audioDisabilityCompliant=None,
        mentalDisabilityCompliant=None,
        motorDisabilityCompliant=None,
        visualDisabilityCompliant=None,
        contact=None,
        isPermanent=True,
    )
    offerers_factories.VenueContactFactory(
        venue=partial_contact_venue, email=None, website="https://example.com", phone_number=None
    )


@atomic()
def create_institutional_website_offer_playlist() -> None:
    criterion = criteria_factories.CriterionFactory(name="home_site_instit")
    image_paths = sorted(pathlib.Path(generic_picture_thumbs.__path__[0]).iterdir())
    portrait_image_paths = image_paths[13:18]

    for i, image_path in zip(range(1, 11), itertools.cycle(portrait_image_paths)):
        offer = offers_factories.OfferFactory(name=f"Offre {i} de la playlist du site institutionnel")
        offers_factories.StockFactory(offer=offer)
        criteria_factories.OfferCriterionFactory(offerId=offer.id, criterionId=criterion.id)

        offers_api.create_mediation(
            user=None,
            offer=offer,
            credit=f"Photographe {i}",
            image_as_bytes=image_path.read_bytes(),
        )


def create_product_with_multiple_images() -> None:
    product = offers_factories.ProductFactory(name="multiple thumbs", subcategoryId=subcategories_v2.LIVRE_PAPIER.id)
    offer = offers_factories.OfferFactory(product=product, name=product.name, subcategoryId=product.subcategoryId)
    offers_factories.StockFactory(offer=offer)
    offers_factories.ProductMediationFactory(
        product=product,
        url="https://storage.googleapis.com/passculture-metier-ehp-testing-assets-fine-grained/thumbs/products/222A",
        imageType=TiteliveImageType.RECTO,
    )
    offers_factories.ProductMediationFactory(
        product=product,
        url="https://storage.googleapis.com/passculture-metier-ehp-testing-assets-fine-grained/thumbs/products/222A_1",
        imageType=TiteliveImageType.VERSO,
    )


def create_discord_users() -> None:
    for i in range(10, 20):
        user = users_factories.BeneficiaryGrant18Factory(
            email=f"discordUser{i}@test.com", firstName=f"discord{i}", lastName=f"user{i}"
        )
        users_factories.DiscordUserFactory(user=user, discordId=None, hasAccess=True)
