import datetime
import itertools
import pathlib
import random

from factory.faker import faker

from pcapi.core.categories import subcategories_v2
from pcapi.core.criteria import factories as criteria_factories
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offers import api as offers_api
from pcapi.core.offers import factories as offers_factories
from pcapi.core.providers import factories as providers_factory
from pcapi.core.providers.titelive_gtl import GTLS
from pcapi.core.users import factories as users_factories
from pcapi.domain.movie_types import movie_types
from pcapi.domain.music_types import music_types
from pcapi.domain.show_types import show_types
from pcapi.repository import atomic
from pcapi.sandboxes.scripts.creators.industrial.create_industrial_gdpr_users import create_industrial_gdpr_users
from pcapi.sandboxes.scripts.creators.industrial.create_industrial_invoices import (
    create_specific_cashflow_batch_without_invoice,
)
from pcapi.sandboxes.scripts.creators.industrial.create_industrial_invoices import create_specific_invoice
from pcapi.sandboxes.scripts.creators.industrial.create_industrial_offer_validation_rules import *
from pcapi.sandboxes.scripts.creators.industrial.create_industrial_offerer_with_custom_reimbursement_rule import (
    create_industrial_offerer_with_custom_reimbursement_rule,
)
from pcapi.sandboxes.scripts.creators.industrial.create_role_permissions import create_roles_with_permissions
from pcapi.sandboxes.scripts.creators.test_cases import venues_mock
import pcapi.sandboxes.thumbs.generic_pictures as generic_picture_thumbs
from pcapi.scripts.venue.venue_label.create_venue_labels import create_venue_labels


Fake = faker.Faker(locale="fr_FR")


def save_test_cases_sandbox() -> None:
    create_offers_with_gtls()
    create_offers_with_same_ean()
    create_venues_across_cities()
    create_offers_for_each_subcategory()
    create_offers_with_same_author()
    create_roles_with_permissions()
    create_industrial_offer_validation_rules()
    create_industrial_gdpr_users()
    create_industrial_offerer_with_custom_reimbursement_rule()
    create_specific_invoice()
    create_specific_cashflow_batch_without_invoice()
    create_venue_labels(sandbox=True)
    create_offers_with_more_extra_data()
    create_venues_with_gmaps_image()
    create_app_beneficiary()
    create_venues_with_practical_info_graphical_edge_cases()
    create_institutional_website_offer_playlist()


def create_offers_with_gtls() -> None:
    librairie_gtl = offerers_factories.VenueFactory(
        name="Librairie des GTls",
        venueTypeCode=offerers_models.VenueTypeCode.BOOKSTORE,
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
        name=product.name,
        subcategoryId=product.subcategoryId,
        description=product.description,
        size=size_per_gtl,
        venue=venue,
        extraData={"gtl_id": gtl_id, "author": Fake.name(), "ean": ean, "editeur": Fake.name()},
    )
    for offer in offers:
        offers_factories.StockFactory(offer=offer)


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
        name=product.name,
        subcategoryId=product.subcategoryId,
        description=product.description,
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
            name=product.name,
            description=product.description,
            subcategoryId=product.subcategoryId,
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
                name=product.name,
                subcategoryId=product.subcategoryId,
                description=product.description,
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
            name=product.name,
            subcategoryId=product.subcategoryId,
            description=product.description,
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
        name=product.name,
        subcategoryId=product.subcategoryId,
        description=product.description,
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


def create_offers_with_more_extra_data() -> None:
    venue_data = random.choice(venues_mock.venues)
    venue = offerers_factories.VenueFactory(
        name="extra_data " + str(venue_data["name"]),
        venueTypeCode=offerers_models.VenueTypeCode.BOOKSTORE,
        latitude=venue_data["latitude"],
        longitude=venue_data["longitude"],
        address=venue_data["address"],
        postalCode=venue_data["postalCode"],
        city=venue_data["city"],
        departementCode=venue_data["departementCode"],
    )
    for _ in range(2):
        create_offers_with_gtl_id(gtl_id=random.choice(list(GTLS)), size_per_gtl=1, venue=venue)
        creat_cine_offer_with_cast(venue)
        create_music_offers(venue)
        create_event_offers(venue)


def create_music_offers(venue: offerers_models.Venue) -> None:
    for subcategory in filter(
        lambda subcategory: subcategories_v2.ExtraDataFieldEnum.MUSIC_TYPE in subcategory.conditional_fields,
        list(subcategories_v2.ALL_SUBCATEGORIES),
    ):
        music_type = random.choice(music_types)
        create_offers_with_extradata(
            venue=venue,
            extra_data={
                "musicType": str(music_type.code),
                "musicSubType": str(random.choice(music_type.children).code),
                "performer": Fake.name(),
            },
            subcategory=subcategory,
        )


def create_event_offers(venue: offerers_models.Venue) -> None:
    for subcategory in subcategories_v2.EVENT_SUBCATEGORIES.values():
        show_type = random.choice(list(show_types))
        create_offers_with_extradata(
            venue=venue,
            extra_data={
                "showType": str(show_type.code),
                "showSubType": str(random.choice(show_type.children).code),
                "performer": Fake.name(),
                "stageDirector": Fake.name(),
                "speaker": Fake.name(),
            },
            subcategory=subcategory,
        )


def creat_cine_offer_with_cast(venue: offerers_models.Venue) -> None:
    create_offers_with_extradata(
        venue=venue,
        extra_data={
            "cast": [Fake.name() for _ in range(random.randint(1, 10))],
            "releaseDate": Fake.date(),
            "genres": [random.choice(movie_types).name for _ in range(random.randint(1, 4))],
            "stageDirector": Fake.name(),
        },
        subcategory=subcategories_v2.SEANCE_CINE,
    )


def create_offers_with_extradata(
    venue: offerers_models.Venue,
    subcategory: subcategories_v2.Subcategory | None = None,
    extra_data: dict | None = None,
    should_create_product: bool = False,
    name: str | None = None,
    description: str | None = None,
) -> None:
    if not subcategory:
        subcategory = random.choice(subcategories_v2.ALL_SUBCATEGORIES)
    offer_adapted_factory = (
        offers_factories.EventOfferFactory if subcategory.is_event else offers_factories.OfferFactory
    )
    if should_create_product:
        product = offers_factories.ProductFactory(
            name=name if name else "product with extradata" + Fake.sentence(nb_words=3, variable_nb_words=True)[:-1],
            subcategoryId=subcategory.id,
            lastProvider=providers_factory.PublicApiProviderFactory(name="BookProvider"),
            extraData=extra_data,
            description=description if description else Fake.paragraph(nb_sentences=5, variable_nb_sentences=True),
        )
        offer = offer_adapted_factory(
            product=product,
            name=product.name,
            subcategoryId=product.subcategoryId,
            description=product.description,
            venue=venue,
            extraData=product.extraData,
        )
    else:
        offer = offer_adapted_factory(
            name=name if name else "offer with extradata" + Fake.sentence(nb_words=3, variable_nb_words=True)[:-1],
            subcategoryId=subcategory.id,
            description=description if description else Fake.paragraph(nb_sentences=5, variable_nb_sentences=True),
            venue=venue,
            extraData=extra_data,
        )
    offers_factories.StockFactory(
        offer=offer,
    )


def create_venues_with_gmaps_image() -> None:
    venue_with_user_image_and_gmaps_image = offerers_factories.VenueFactory(
        isPermanent=True,
        name="venue_with_user_image_and_gmaps_image",
        _bannerUrl="https://storage.googleapis.com/passculture-metier-ehp-testing-assets-fine-grained/thumbs/offerers/FY",
    )
    offerers_factories.GooglePlacesInfoFactory(
        bannerUrl="https://storage.googleapis.com/passculture-metier-ehp-testing-assets-fine-grained/assets/Google_Maps_Logo_2020.png",
        venue=venue_with_user_image_and_gmaps_image,
    )

    venue_without_user_image_and_with_gmaps_image = offerers_factories.VenueFactory(
        isPermanent=True,
        name="venue_without_user_image_and_with_gmaps_image",
        _bannerUrl=None,
    )
    offerers_factories.GooglePlacesInfoFactory(
        bannerUrl="https://storage.googleapis.com/passculture-metier-ehp-testing-assets-fine-grained/assets/Google_Maps_Logo_2020.png",
        venue=venue_without_user_image_and_with_gmaps_image,
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
        address=(
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
