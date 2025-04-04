import datetime
import itertools
import pathlib
import random
import uuid

from dateutil.relativedelta import relativedelta
from factory.faker import faker

from pcapi import settings
from pcapi.connectors import thumb_storage
from pcapi.core.achievements import factories as achievements_factories
from pcapi.core.achievements import models as achievements_models
from pcapi.core.artist import factories as artist_factories
from pcapi.core.artist.models import ArtistType
from pcapi.core.bookings import factories as bookings_factories
from pcapi.core.categories import subcategories
from pcapi.core.criteria import factories as criteria_factories
from pcapi.core.finance.factories import RecreditFactory
from pcapi.core.finance.models import DepositType
from pcapi.core.finance.models import RecreditType
from pcapi.core.fraud import factories as fraud_factories
from pcapi.core.fraud.models import FraudCheckType
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offers import api as offers_api
from pcapi.core.offers import factories as offers_factories
from pcapi.core.offers.models import TiteliveImageType
from pcapi.core.providers import factories as providers_factories
from pcapi.core.providers.titelive_gtl import GTLS
from pcapi.core.reactions.factories import ReactionFactory
from pcapi.core.reactions.models import ReactionTypeEnum
from pcapi.core.users import api as users_api
from pcapi.core.users import factories as users_factories
from pcapi.repository import atomic
from pcapi.sandboxes.scripts.creators.industrial.create_industrial_gdpr_users import create_industrial_gdpr_users
from pcapi.sandboxes.scripts.creators.industrial.create_industrial_invoices import (
    create_specific_cashflow_batch_without_invoice,
)
from pcapi.sandboxes.scripts.creators.industrial.create_industrial_invoices import create_free_invoice
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
    create_artists()
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
    create_free_invoice()
    create_specific_cashflow_batch_without_invoice()
    create_venue_labels(sandbox=True)
    create_venues_with_gmaps_image()
    create_app_beneficiaries()
    create_venues_with_practical_info_graphical_edge_cases()
    create_institutional_website_offer_playlist()
    create_product_with_multiple_images()
    create_discord_users()
    create_users_with_reactions()
    create_user_that_booked_some_cinema()  # to suggest reactions on cinema bookings
    create_users_for_credit_v3_tests()


def create_users_for_credit_v3_tests() -> None:
    ### 'static' users

    ## 18yo user, beneficiary, started before decree
    users_factories.BeneficiaryFactory(
        firstName="User18",
        lastName="Inscriptionavantdecret",
        email="user18avantdecret@test.com",
        age=18,
        deposit__dateCreated=settings.CREDIT_V3_DECREE_DATETIME - datetime.timedelta(days=1),
    )

    ## 18yo user, beneficiary, started after decree
    users_factories.BeneficiaryFactory(
        firstName="User18",
        lastName="Inscriptionapresdecret",
        email="user18apresdecret@test.com",
        age=18,
        deposit__dateCreated=settings.CREDIT_V3_DECREE_DATETIME + datetime.timedelta(days=1),
    )

    ## 17yo user, beneficiary, started before decree
    users_factories.BeneficiaryFactory(
        firstName="User17",
        lastName="Inscriptionavantdecret",
        email="user17avantdecret@test.com",
        age=17,
        deposit__dateCreated=settings.CREDIT_V3_DECREE_DATETIME - datetime.timedelta(days=1),
    )

    ## 17yo user, beneficiary, started after decree
    users_factories.BeneficiaryFactory(
        firstName="User17",
        lastName="Inscriptionapresdecret",
        email="user17apresdecret@test.com",
        age=17,
        deposit__dateCreated=settings.CREDIT_V3_DECREE_DATETIME + datetime.timedelta(days=1),
    )

    ## 16yo user, beneficiary, started before decree
    users_factories.BeneficiaryFactory(
        firstName="User16",
        lastName="Inscriptionavantdecret",
        email="user16avantdecret@test.com",
        age=16,
        deposit__dateCreated=settings.CREDIT_V3_DECREE_DATETIME - datetime.timedelta(days=1),
    )

    ## 16yo user, started after decree
    users_factories.BaseUserFactory(
        firstName="User16", lastName="Inscriptionapresdecret", email="user16apresdecret@test.com", age=16
    )

    ## 15yo user, beneficiary, started before decree
    users_factories.BeneficiaryFactory(
        firstName="User15",
        lastName="Inscriptionavantdecret",
        email="user15avantdecret@test.com",
        age=15,
        deposit__dateCreated=settings.CREDIT_V3_DECREE_DATETIME - datetime.timedelta(days=1),
    )

    ## 15yo user, beneficiary, started after decree
    users_factories.BaseUserFactory(
        firstName="User15", lastName="Inscriptionapresdecret", email="user15apresdecret@test.com", age=15
    )

    ### Users who had a deposit underage before the decree ###

    ## 18yo user, beneficiary, with birthday before decree
    one_day_before_decree = settings.CREDIT_V3_DECREE_DATETIME - datetime.timedelta(days=1)
    user_birthdate = one_day_before_decree - relativedelta(years=18)
    first_activation_date = one_day_before_decree - relativedelta(years=3)  # User created at 15 yo

    user18_redepotavantdecret = users_factories.BeneficiaryFactory(
        firstName="User18",
        lastName="Redepotavantdecret",
        email="user18redepotavantdecret@test.com",
        validatedBirthDate=user_birthdate,
        deposit__dateCreated=one_day_before_decree,
        dateCreated=first_activation_date,
    )
    # then add the previous deposit they would have had at 15
    user18_redepotavantdecret_underage_deposit = users_factories.DepositGrantFactory(
        user=user18_redepotavantdecret,
        dateCreated=first_activation_date,
        type=DepositType.GRANT_15_17,
        amount=20 + 30 + 30,
        expirationDate=user_birthdate + relativedelta(years=18),
    )
    RecreditFactory(
        deposit=user18_redepotavantdecret_underage_deposit, amount=30, recreditType=RecreditType.RECREDIT_16
    )
    RecreditFactory(
        deposit=user18_redepotavantdecret_underage_deposit, amount=30, recreditType=RecreditType.RECREDIT_17
    )

    ## 18yo user, beneficiary, with birthday after decree
    one_day_after_decree = settings.CREDIT_V3_DECREE_DATETIME + datetime.timedelta(days=1)
    user_birthdate = one_day_after_decree - relativedelta(years=18)
    first_activation_date = one_day_after_decree - relativedelta(years=3)  # User created at 15 yo

    user18_redepotapresdecret = users_factories.BeneficiaryFactory(
        firstName="User18",
        lastName="Redepotavantdecret",
        email="user18redepotapresdecret@test.com",
        dateCreated=first_activation_date,
        age=17,  # set at 17yo and correct at 18yo afterwards
        validatedBirthDate=one_day_after_decree.date() - relativedelta(years=17),
    )
    # then update the deposit they would have had at 15
    RecreditFactory(deposit=user18_redepotapresdecret.deposit, amount=30, recreditType=RecreditType.RECREDIT_16)
    RecreditFactory(deposit=user18_redepotapresdecret.deposit, amount=30, recreditType=RecreditType.RECREDIT_17)
    user18_redepotapresdecret.deposit.expirationDate = user_birthdate + relativedelta(years=21)
    user18_redepotapresdecret.deposit.amount = 20 + 30 + 30  # 20 initial amount + 2 recredits above

    # add a reimbursed booking to old deposit
    bookings_factories.ReimbursedBookingFactory(user=user18_redepotapresdecret, quantity=1, amount=15)

    # Set real age to 18 via admin action
    users_api.update_user_info(
        user18_redepotapresdecret,
        author=users_factories.AdminFactory(),
        validated_birth_date=user_birthdate.date(),
    )

    # finish missing steps
    fraud_factories.BeneficiaryFraudCheckFactory(user=user18_redepotapresdecret, type=FraudCheckType.UBBLE)
    fraud_factories.PhoneValidationFraudCheckFactory(user=user18_redepotapresdecret)
    user18_redepotapresdecret.phoneNumber = "+33612345678"
    fraud_factories.ProfileCompletionFraudCheckFactory(user=user18_redepotapresdecret)
    fraud_factories.HonorStatementFraudCheckFactory(user=user18_redepotapresdecret)

    ## 17yo user, beneficiary, with birthday before decree
    first_activation_date = one_day_before_decree - relativedelta(years=2)  # User created at 15 yo
    user_birthdate = one_day_before_decree - relativedelta(years=17)
    user_17_bday_before_decree = users_factories.BeneficiaryFactory(
        firstName="User17",
        lastName="Anniversaireavantreforme",
        email="user17anniversaireavantdecret@test.com",
        dateCreated=first_activation_date,
        deposit__amount=20 + 30 + 30,
        validatedBirthDate=user_birthdate,
    )
    RecreditFactory(deposit=user_17_bday_before_decree.deposit, amount=30, recreditType=RecreditType.RECREDIT_16)
    RecreditFactory(deposit=user_17_bday_before_decree.deposit, amount=30, recreditType=RecreditType.RECREDIT_17)

    ## 17yo user, beneficiary, with birthday after decree
    first_activation_date = one_day_after_decree - relativedelta(years=2)  # User created at 15 yo
    user_17_after_decree = users_factories.BeneficiaryFactory(
        firstName="User17",
        lastName="Anniversaireaprèsréforme",
        email="user17anniversaireapresdecret@test.com",
        age=16,  # set at 16yo and correct at 17yo afterwards
        validatedBirthDate=one_day_after_decree.date() - relativedelta(years=16),
        dateCreated=first_activation_date,
        deposit__amount=20 + 30,
    )
    # Add recredit 16
    RecreditFactory(deposit=user_17_after_decree.deposit, amount=30, recreditType=RecreditType.RECREDIT_16)
    # Set real age to 17
    user_17_after_decree.validatedBirthDate = (one_day_after_decree - relativedelta(years=17)).date()

    ## 16yo user, beneficiary, with birthday before decree
    user_16_before_decree = users_factories.BeneficiaryFactory(
        firstName="User16",
        lastName="Anniversaireavantreforme",
        email="user16anniversaireavantdecret@test.com",
        validatedBirthDate=one_day_before_decree - relativedelta(years=16),
        deposit__dateCreated=settings.CREDIT_V3_DECREE_DATETIME - datetime.timedelta(days=1),
        deposit__amount=20 + 30,
    )
    # Set Recredits that happened before the decree
    RecreditFactory(deposit=user_16_before_decree.deposit, amount=30, recreditType=RecreditType.RECREDIT_16)

    ## 16yo user, beneficiary, with birthday after decree
    user_16_after_decree = users_factories.BeneficiaryFactory(
        firstName="User16",
        lastName="Anniversaireaprèsréforme",
        email="user16anniversaireapresdecret@test.com",
        age=15,  # create user at 15 yo
        deposit__dateCreated=settings.CREDIT_V3_DECREE_DATETIME - datetime.timedelta(days=1),
    )
    # Set real age to 16
    user_16_after_decree.validatedBirthDate = (one_day_after_decree - relativedelta(years=16)).date()


def create_artists() -> None:
    venue = offerers_factories.VenueFactory(
        name="Lieu avec artistes", venueTypeCode=offerers_models.VenueTypeCode.BOOKSTORE
    )

    # Artist 1 : writer
    artist_1 = artist_factories.ArtistFactory(
        name="Virginie Despentes",
        description="écrivaine et réalisatrice française",
        image="http://commons.wikimedia.org/wiki/Special:FilePath/Virginie%20Despentes%202012.jpg",
        image_license="CC BY-SA 3.0",
        image_license_url="https://creativecommons.org/licenses/by-sa/3.0",
    )
    for _ in range(10):
        product = offers_factories.ProductFactory(subcategoryId=subcategories.LIVRE_PAPIER.id)
        offers_factories.OfferFactory(product=product, venue=venue)
        offers_factories.ArtistProductLinkFactory(
            artist_id=artist_1.id, product_id=product.id, artist_type=ArtistType.AUTHOR
        )
    artist_factories.ArtistAliasFactory(artist_id=artist_1.id, artist_alias_name="Virginie Despente")

    # Artist 2 : singer
    artist_2 = artist_factories.ArtistFactory(
        name="Avril Lavigne",
        description="chanteuse canadienne",
        image="http://commons.wikimedia.org/wiki/Special:FilePath/Glaston2024%202806%20300624%20%28129%20of%20173%29%20%28cropped%29.jpg",
        image_license="CC BY 2.0",
        image_license_url="https://creativecommons.org/licenses/by/2.0",
    )
    for _ in range(10):
        product = offers_factories.ProductFactory(subcategoryId=subcategories.SUPPORT_PHYSIQUE_MUSIQUE_VINYLE.id)
        offers_factories.OfferFactory(product=product, venue=venue)
        offers_factories.ArtistProductLinkFactory(
            artist_id=artist_2.id, product_id=product.id, artist_type=ArtistType.PERFORMER
        )
    artist_factories.ArtistAliasFactory(artist_id=artist_2.id, artist_alias_name="Lavigne Avril")

    # Artist 3 : other
    artist_3 = artist_factories.ArtistFactory(
        name="Marina Rollman",
        description="humoriste suisse",
        image="http://commons.wikimedia.org/wiki/Special:FilePath/Marina-Rollman-20150710-023%20%2819415372158%29.jpg",
        image_license="CC BY-SA 2.0",
        image_license_url="https://creativecommons.org/licenses/by-sa/2.0",
    )
    for _ in range(10):
        product = offers_factories.ProductFactory(subcategoryId=subcategories.SEANCE_CINE.id)
        offers_factories.OfferFactory(product=product, venue=venue)
        offers_factories.ArtistProductLinkFactory(
            artist_id=artist_3.id, product_id=product.id, artist_type=ArtistType.PERFORMER
        )
    artist_factories.ArtistAliasFactory(artist_id=artist_3.id, artist_alias_name="Rollman Marina")

    _create_library_with_writers()


def _create_library_with_writers() -> None:
    venue = offerers_factories.VenueFactory(
        name="Librairie des artistes", venueTypeCode=offerers_models.VenueTypeCode.BOOKSTORE
    )
    artists = [
        artist_factories.ArtistFactory(
            name="Annie Ernaux",
            description="Professeure de lettres et écrivaine française",
            image="https://upload.wikimedia.org/wikipedia/commons/a/a6/Annie_Ernaux_in_2022_%289_av_11%29.jpg",
            image_license="Creative Commons Attribution-Share Alike 4.0",
            image_license_url="https://creativecommons.org/licenses/by-sa/4.0/",
        ),
        artist_factories.ArtistFactory(
            name="George Sand",
            description="Romancière, dramaturge, épistolière, critique littéraire et journaliste française",
            image="https://upload.wikimedia.org/wikipedia/commons/e/ee/George_Sand.PNG",
        ),
        artist_factories.ArtistFactory(
            name="Miguel de Cervantes",
            description="Romancier, poète et dramaturge espagnol",
            image="https://upload.wikimedia.org/wikipedia/commons/4/47/Miguel_de_Cervantes_2.jpg",
        ),
        artist_factories.ArtistFactory(
            name="Jane Austen",
            description="Romancière et femme de lettres anglaise",
        ),
        artist_factories.ArtistFactory(
            name="Ernest Hemingway",
            description="Écrivain, journaliste et correspondant de guerre américain",
            image="https://upload.wikimedia.org/wikipedia/commons/2/28/ErnestHemingway.jpg",
        ),
        artist_factories.ArtistFactory(),
        artist_factories.ArtistFactory(),
        artist_factories.ArtistFactory(),
        artist_factories.ArtistFactory(),
        artist_factories.ArtistFactory(),
    ]

    image_paths = itertools.cycle(pathlib.Path(generic_picture_thumbs.__path__[0]).iterdir())
    for artist in artists:
        for num in range(5):
            product = offers_factories.ProductFactory(
                name=f"Livre - {artist.name} - {num + 1}", subcategoryId=subcategories.LIVRE_PAPIER.id
            )
            image_path = next(image_paths)
            mediation = offers_factories.ProductMediationFactory(product=product, imageType=TiteliveImageType.RECTO)
            thumb_storage.create_thumb(product, image_path.read_bytes(), keep_ratio=True, object_id=mediation.uuid)
            offers_factories.ArtistProductLinkFactory(
                artist_id=artist.id, product_id=product.id, artist_type=ArtistType.AUTHOR
            )
            offer = offers_factories.OfferFactory(product=product, venue=venue)
            offers_factories.StockFactory(offer=offer)


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
        banId="63103_0040_00013",
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
        banId="85191_0940_00011",
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
        subcategoryId=subcategories.LIVRE_PAPIER.id,
        lastProvider=providers_factories.PublicApiProviderFactory(name="BookProvider"),
        idAtProviders=ean,
        extraData={"gtl_id": gtl_id, "author": Fake.name(), "ean": ean},
    )
    offers = offers_factories.OfferFactory.create_batch(
        product=product,
        size=size_per_gtl,
        venue=venue,
    )
    for offer in offers:
        offers_factories.StockFactory(offer=offer)


def create_offers_with_same_ean() -> None:
    offers = []
    product = offers_factories.ProductFactory(
        name="Le livre du pass Culture",
        subcategoryId=subcategories.LIVRE_PAPIER.id,
        lastProvider=providers_factories.PublicApiProviderFactory(name="BookProvider"),
    )
    for venue_data in venues_mock.venues:
        offers.append(
            offers_factories.OfferFactory(
                product=product,
                subcategoryId=subcategories.LIVRE_PAPIER.id,
                venue=offerers_factories.VenueFactory(
                    name=venue_data["name"],
                    venueTypeCode=offerers_models.VenueTypeCode.BOOKSTORE,
                    latitude=venue_data["latitude"],
                    longitude=venue_data["longitude"],
                    street=venue_data["address"],
                    postalCode=venue_data["postalCode"],
                    city=venue_data["city"],
                    departementCode=venue_data["departementCode"],
                    banId=venue_data["banId"],
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
        subcategoryId=subcategories.LIVRE_PAPIER.id,
        lastProvider=providers_factories.PublicApiProviderFactory(name="BookProvider"),
        idAtProviders=ean,
        extraData={"ean": ean, "author": author},
    )
    offer = offers_factories.OfferFactory(
        product=product,
        name=product.name,
        subcategoryId=product.subcategoryId,
        venue=venue,
    )
    offers_factories.StockFactory(quantity=random.randint(10, 100), offer=offer)


def create_offer_and_stocks_for_cinemas(
    venues: list[offerers_models.Venue], products: list[offers_models.Product]
) -> None:
    for venue in venues:
        for idx, product in enumerate(products):
            movie_offer = offers_factories.OfferFactory(
                name=product.name,
                product=product,
                subcategoryId=subcategories.SEANCE_CINE.id,
                venue=venue,
                extraData=product.extraData,
            )
            mediation = offers_factories.MediationFactory(offer=movie_offer)
            store_public_object_from_sandbox_assets("thumbs", mediation, movie_offer.subcategoryId)

            product_stocks = []
            for daydelta in range(0, 20, 2):
                day = datetime.date.today() + datetime.timedelta(days=daydelta)
                for hour in (5, 11, 17, 21):
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
    products = create_movie_products()
    create_offer_and_stocks_for_cinemas(venues, products)


def create_movie_products(offset: int = 0) -> list[offers_models.Product]:
    return [
        offers_factories.ProductFactory(
            subcategoryId=subcategories.SEANCE_CINE.id,
            description=f"Description du film {i}",
            name=f"Film {i}",
            extraData={"allocineId": 100_000 + i},
            durationMinutes=115 + i,
        )
        for i in range(1 + offset, 6 + offset)
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
            banId=venue_data["banId"],
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
                banId=venue["banId"],
            )
            for _ in range(7):
                offer = offers_factories.OfferFactory(
                    venue=venue,
                    product=None,
                    subcategoryId=random.choice(subcategories.ALL_SUBCATEGORIES).id,
                    name=Fake.sentence(nb_words=3, variable_nb_words=True)[:-1],
                    description=Fake.paragraph(nb_sentences=5, variable_nb_sentences=True),
                    url=None,
                )
                for _ in range(random.randint(1, 10)):
                    offers_factories.StockFactory(quantity=random.randint(10, 100), offer=offer)

            for _ in range(3):
                event_offer = offers_factories.EventOfferFactory(
                    venue=venue,
                    product=None,
                    subcategoryId=random.choice(list(subcategories.EVENT_SUBCATEGORIES)),
                    name=Fake.sentence(nb_words=3, variable_nb_words=True)[:-1],
                    description=Fake.paragraph(nb_sentences=5, variable_nb_sentences=True),
                    url=None,
                )
                for _ in range(random.randint(1, 10)):
                    offers_factories.EventStockFactory(
                        quantity=random.randint(10, 100),
                        offer=event_offer,
                        beginningDatetime=datetime.datetime.utcnow()
                        + datetime.timedelta(
                            days=random.randint(30, 59),
                            hours=random.randint(1, 23),
                            minutes=random.randint(1, 59),
                            seconds=random.randint(1, 59),
                        ),
                    )


def create_offers_for_each_subcategory() -> None:
    for subcategory in subcategories.ALL_SUBCATEGORIES:
        for i in range(1, 11):
            is_free = i % 2
            is_in_Paris = i < 6  # else it will be Marseille
            if subcategory.id in subcategories.EVENT_SUBCATEGORIES:
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
        subcategoryId=subcategories.LIVRE_PAPIER.id,
    )
    for venue in venues[:3]:
        offer = offers_factories.OfferFactory(
            product=product,
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
            subcategoryId=subcategories.LIVRE_PAPIER.id,
            extraData={"ean": ean, "author": author},
        )
        for venue in venues:
            offer = offers_factories.OfferFactory(
                product=product,
                venue=venue,
            )
            offers_factories.StockFactory(quantity=random.randint(10, 100), offer=offer)

    for tome in range(11, 16):
        ean = Fake.ean13()
        product = offers_factories.ProductFactory(
            name="One Piece tome " + str(tome),
            subcategoryId=subcategories.LIVRE_PAPIER.id,
            extraData={"ean": ean, "author": author},
        )
        offer = offers_factories.OfferFactory(
            product=product,
            venue=venues[3],
        )
        offers_factories.StockFactory(quantity=random.randint(10, 100), offer=offer)


def create_multiauthors_books(venues: list[offerers_models.Venue]) -> None:
    # multiple authors
    authors = [Fake.name() for _ in range(4)]
    ean = Fake.ean13()
    product = offers_factories.ProductFactory(
        name="multiauth",
        subcategoryId=subcategories.LIVRE_PAPIER.id,
        extraData={"ean": ean, "author": ", ".join(authors)},
    )
    offer = offers_factories.OfferFactory(
        product=product,
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
            subcategoryId=random.choice(subcategories.ALL_SUBCATEGORIES).id,
            name=Fake.sentence(nb_words=3, variable_nb_words=True)[:-1],
            description=Fake.paragraph(nb_sentences=5, variable_nb_sentences=True),
            url=None,
        )
    )
    offers_factories.StockFactory(
        offer=offers_factories.OfferFactory(
            venue=venue_without_user_image_and_with_gmaps_image,
            product=None,
            subcategoryId=random.choice(subcategories.ALL_SUBCATEGORIES).id,
            name=Fake.sentence(nb_words=3, variable_nb_words=True)[:-1],
            description=Fake.paragraph(nb_sentences=5, variable_nb_sentences=True),
            url=None,
        )
    )
    offers_factories.StockFactory(
        offer=offers_factories.OfferFactory(
            venue=venue_with_no_images,
            product=None,
            subcategoryId=random.choice(subcategories.ALL_SUBCATEGORIES).id,
            name=Fake.sentence(nb_words=3, variable_nb_words=True)[:-1],
            description=Fake.paragraph(nb_sentences=5, variable_nb_sentences=True),
            url=None,
        )
    )


def create_app_beneficiaries() -> None:
    users_factories.BeneficiaryGrant18Factory(
        email="dev-tests-e2e@passculture.team",
        firstName=Fake.first_name(),
        lastName=Fake.last_name(),
        needsToFillCulturalSurvey=False,
    )

    user_with_achievements = users_factories.BeneficiaryGrant18Factory(
        email="achievement@example.com",
        firstName=Fake.first_name(),
        lastName=Fake.last_name(),
        needsToFillCulturalSurvey=False,
    )
    achievements_factories.AchievementFactory(
        user=user_with_achievements,
        name=achievements_models.AchievementEnum.FIRST_BOOK_BOOKING,
        unlockedDate=datetime.datetime.utcnow(),
    )
    achievements_factories.AchievementFactory(
        user=user_with_achievements,
        name=achievements_models.AchievementEnum.FIRST_SHOW_BOOKING,
        unlockedDate=datetime.datetime.utcnow(),
        seenDate=datetime.datetime.utcnow(),
    )
    achievements_factories.AchievementFactory(
        user=user_with_achievements,
        name=achievements_models.AchievementEnum.FIRST_ART_LESSON_BOOKING,
        unlockedDate=datetime.datetime.utcnow(),
        seenDate=datetime.datetime.utcnow(),
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
    product = offers_factories.ProductFactory(
        name="multiple thumbs",
        subcategoryId=subcategories.LIVRE_PAPIER.id,
        extraData={"ean": "9999999999999"},
    )
    offer = offers_factories.OfferFactory(product=product, name=product.name, subcategoryId=product.subcategoryId)
    offers_factories.StockFactory(offer=offer)
    offers_factories.ProductMediationFactory(
        product=product,
        uuid="222A",
        imageType=TiteliveImageType.RECTO,
    )
    offers_factories.ProductMediationFactory(
        product=product,
        uuid="222A_1",
        imageType=TiteliveImageType.VERSO,
    )


def create_discord_users() -> None:
    for i in range(10, 20):
        user = users_factories.BeneficiaryFactory(
            email=f"discordUser{i}@test.com", firstName=f"discord{i}", lastName=f"user{i}"
        )
        users_factories.DiscordUserFactory(user=user, discordId=None, hasAccess=True)


def create_users_with_reactions() -> None:
    # Test case 1 : a user booked an offer and reacted to it
    #   - user_1 booked and reacted to offers linked to a product
    #   - user_2 booked and reacted to offers not linked to a product
    user_1 = users_factories.BeneficiaryFactory(email="catherine.foundling@example.com")
    user_2 = users_factories.BeneficiaryFactory(email="hakram.ofthehowlingwolves@example.com")

    reactions_to_add = [ReactionTypeEnum.LIKE, ReactionTypeEnum.DISLIKE, ReactionTypeEnum.NO_REACTION, None]
    for reaction_type in reactions_to_add:
        # USER 1
        product = offers_factories.ProductFactory()
        stock = offers_factories.StockFactory(offer__product=product)
        bookings_factories.UsedBookingFactory(stock=stock, user=user_1)
        if reaction_type is not None:
            ReactionFactory(user=user_1, product=product, reactionType=reaction_type)

        # USER 2
        stock = offers_factories.StockFactory()
        bookings_factories.UsedBookingFactory(stock=stock, user=user_2)
        if reaction_type is not None:
            ReactionFactory(user=user_2, offer=stock.offer, reactionType=reaction_type)


def create_user_that_booked_some_cinema() -> None:
    seance_cine_start = datetime.datetime.utcnow() - datetime.timedelta(hours=25)
    stock = offers_factories.StockFactory(
        beginningDatetime=seance_cine_start, quantity=100, offer__subcategoryId=subcategories.SEANCE_CINE.id
    )
    for i in range(10):
        user_email = f"ella-reserveducine-{i}@example.com"
        user = users_factories.BeneficiaryFactory(email=user_email)
        bookings_factories.UsedBookingFactory(user=user, stock=stock, dateUsed=seance_cine_start)
