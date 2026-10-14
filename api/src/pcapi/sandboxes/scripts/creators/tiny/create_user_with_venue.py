import datetime
import logging
import pathlib

from pcapi.connectors import thumb_storage
from pcapi.core.artist import factories as artist_factories
from pcapi.core.artist import models as artist_models
from pcapi.core.bookings.factories import BookingFactory
from pcapi.core.categories import subcategories
from pcapi.core.discoveries import models as discoveries_models
from pcapi.core.educational import factories as educational_factories
from pcapi.core.educational import models as educational_models
from pcapi.core.educational.constants import ALL_INTERVENTION_AREA
from pcapi.core.educational.repository import find_educational_institution_by_uai_code
from pcapi.core.educational.utils import UAI_FOR_FAKE_TOKEN
from pcapi.core.offerers import api as offerers_api
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offerers.factories import UserOffererFactory
from pcapi.core.offerers.factories import VenueFactory
from pcapi.core.offers import factories as offers_factories
from pcapi.core.offers import models as offers_models
from pcapi.core.offers.factories import EventOfferFactory
from pcapi.core.offers.factories import EventStockFactory
from pcapi.core.users import factories as users_factories
from pcapi.core.users import models as users_models
from pcapi.core.wishlists import models as wishlists_models
from pcapi.models import db
from pcapi.sandboxes.scripts.utils.storage_utils import add_image_to_offer
from pcapi.sandboxes.scripts.utils.storage_utils import add_image_to_work
from pcapi.sandboxes.scripts.utils.storage_utils import read_sandbox_mediation_asset
from pcapi.sandboxes.thumbs import generic_pictures
from pcapi.utils import date as date_utils


logger = logging.getLogger(__name__)


def _create_tiny_works_and_artists(offer: offers_models.Offer) -> None:
    director = artist_factories.ArtistFactory.create(name="Camille Martin", main_role="stage_director")
    performer = artist_factories.ArtistFactory.create(name="Alex Dubois", main_role="performer")
    author = artist_factories.ArtistFactory.create(name="Lou Bernard", main_role="author")
    performance = discoveries_models.Work(
        title=offer.name, media_type=discoveries_models.WorkMediaType.PERFORMING_ART, release_year=2026
    )
    book = discoveries_models.Work(title="Les petites aventures", media_type=discoveries_models.WorkMediaType.BOOK)
    album = discoveries_models.Work(title="Petites melodies", media_type=discoveries_models.WorkMediaType.MUSIC)
    product = offers_models.Product(
        name=offer.name,
        subcategoryId=offer.subcategoryId,
        description=offer.description,
        durationMinutes=offer.durationMinutes,
        extraData=dict(offer.extraData) if offer.extraData is not None else None,
        work=performance,
    )
    offer.product = product
    db.session.add_all(
        [
            product,
            discoveries_models.WorkArtist(work=performance, artist=director, role="stage_director"),
            discoveries_models.WorkArtist(work=performance, artist=performer, role="performer"),
            discoveries_models.WorkArtist(work=book, artist=author, role="author"),
            discoveries_models.WorkArtist(work=album, artist=performer, role="performer"),
        ]
    )
    db.session.flush()
    add_image_to_work(performance, subcategories.CONFERENCE.id)
    add_image_to_work(book, subcategories.LIVRE_PAPIER.id)
    add_image_to_work(album, subcategories.SUPPORT_PHYSIQUE_MUSIQUE_CD.id)
    for artist, artist_type in (
        (director, artist_models.ArtistType.STAGE_DIRECTOR),
        (performer, artist_models.ArtistType.PERFORMER),
    ):
        db.session.add_all(
            [
                artist_models.ArtistProductLink(artist_id=artist.id, product_id=product.id, artist_type=artist_type),
                artist_models.ArtistOfferLink(artist_id=artist.id, offer_id=offer.id, artist_type=artist_type),
            ]
        )
    db.session.flush()
    logger.info(
        "created tiny works %s and artists %s",
        [performance.id, book.id, album.id],
        [director.id, performer.id, author.id],
    )


def _create_tiny_artist_works(
    name: str, role: str, titles: list[tuple[str, int]], beneficiary: users_models.User
) -> tuple[artist_models.Artist, list[discoveries_models.Work]]:
    artist = db.session.query(artist_models.Artist).filter_by(name=name).first()
    if artist is None:
        artist = artist_factories.ArtistFactory.create(
            name=name, main_role=role, wikidata_id=None, image=None, description=None
        )
    is_film = role == "film_director"
    subcategory_id = subcategories.SEANCE_CINE.id if is_film else subcategories.LIVRE_PAPIER.id
    db.session.add(discoveries_models.Discovery(user=beneficiary, artist=artist))
    works = []
    for title, year in titles:
        work = discoveries_models.Work(
            title=title,
            release_year=year,
            media_type=discoveries_models.WorkMediaType.FILM if is_film else discoveries_models.WorkMediaType.BOOK,
        )
        db.session.add_all(
            [
                discoveries_models.WorkArtist(work=work, artist=artist, role=role),
                discoveries_models.Discovery(user=beneficiary, work=work),
            ]
        )
        db.session.flush()
        add_image_to_work(work, subcategory_id)
        if artist.image is None:
            artist.image = work.visual_url
        works.append(work)
    return artist, works


def _create_tiny_work_offer(work: discoveries_models.Work, venue: offerers_models.Venue) -> None:
    is_film = work.media_type == discoveries_models.WorkMediaType.FILM
    subcategory_id = subcategories.SEANCE_CINE.id if is_film else subcategories.LIVRE_PAPIER.id
    product = offers_models.Product(name=work.title, subcategoryId=subcategory_id, work=work)
    offer = offers_factories.OfferFactory.create(venue=venue, product=product)
    if is_film:
        EventStockFactory.create(offer=offer, quantity=20, price=8)
    else:
        offers_factories.ThingStockFactory.create(offer=offer, quantity=10, price=15)
    artist = work.artist_links[0].artist
    artist_type = artist_models.ArtistType.FILM_DIRECTOR if is_film else artist_models.ArtistType.AUTHOR
    db.session.add_all(
        [
            artist_models.ArtistProductLink(artist_id=artist.id, product_id=product.id, artist_type=artist_type),
            artist_models.ArtistOfferLink(artist_id=artist.id, offer_id=offer.id, artist_type=artist_type),
        ]
    )
    mediation = offers_factories.MediationFactory.create(offer=offer)
    thumb_storage.create_thumb(mediation, read_sandbox_mediation_asset(subcategory_id), keep_ratio=True)


def _create_tiny_public_wishlists(venue: offerers_models.Venue) -> None:
    beneficiary = users_factories.BeneficiaryFactory.create(
        email="ouiche.tiny@example.com", firstName="Sakura", lastName="Martin"
    )
    catalogue = [
        ("Hayao Miyazaki", "film_director", [("Le Voyage de Chihiro", 2001), ("Princesse Mononoké", 1997)]),
        ("Akira Kurosawa", "film_director", [("Les Sept Samouraïs", 1954), ("Rashōmon", 1950)]),
        ("Satoshi Kon", "film_director", [("Paprika", 2006), ("Perfect Blue", 1997)]),
        ("Christopher Nolan", "film_director", [("Inception", 2010), ("Interstellar", 2014)]),
        ("Bong Joon-ho", "film_director", [("Parasite", 2019), ("Memories of Murder", 2003)]),
        ("Haruki Murakami", "author", [("Kafka sur le rivage", 2002), ("1Q84", 2009)]),
        ("Kōbō Abe", "author", [("La Femme des sables", 1962), ("La Face d'un autre", 1964)]),
        ("George Orwell", "author", [("1984", 1949), ("La Ferme des animaux", 1945)]),
        ("Aldous Huxley", "author", [("Le Meilleur des mondes", 1932), ("Les Portes de la perception", 1954)]),
        ("Alain Damasio", "author", [("La Horde du Contrevent", 2004), ("Les Furtifs", 2019)]),
    ]
    films: list[discoveries_models.Work] = []
    books: list[discoveries_models.Work] = []
    japanese_works: list[discoveries_models.Work] = []
    japanese_artists: list[artist_models.Artist] = []
    for artist_index, (name, role, titles) in enumerate(catalogue):
        artist, works = _create_tiny_artist_works(name, role, titles, beneficiary)
        collection = films if role == "film_director" else books
        collection.extend(works)
        if artist_index in (0, 1, 2, 5, 6):
            japanese_artists.append(artist)
            japanese_works.extend(works)
    for work in films[:3] + books[:3]:
        _create_tiny_work_offer(work, venue)
    for name, works, artists in (
        ("10 films à voir absolument", films, []),
        ("Les livres m'ayant retourner le cerveau", books, []),
        ("Découverte du Japon", japanese_works, japanese_artists),
    ):
        wishlist = wishlists_models.Wishlist(
            user=beneficiary, name=name, visibility=wishlists_models.WishlistVisibility.PUBLIC
        )
        db.session.add(wishlist)
        for position, work in enumerate(works):
            db.session.add(wishlists_models.WishlistItem(wishlist=wishlist, work=work, position=position))
        for position, artist in enumerate(artists, start=len(works)):
            db.session.add(wishlists_models.WishlistItem(wishlist=wishlist, artist=artist, position=position))
    db.session.flush()
    logger.info("Created public ouiche lists for beneficiary %s", beneficiary.email)


def create_tiny_venue() -> None:
    logger.info("start create tiny venue")
    email = "tom.pouce@example.com"
    user_offerer = UserOffererFactory.create(
        user__email=email, offerer__name="Ma petite entreprise", user__firstName="Tom", user__lastName="Pouce"
    )
    logger.info(f"You can connect to pro with : {email}")
    venue = VenueFactory.create(
        name="Petit lieu",
        managingOfferer=user_offerer.offerer,
        adageId="123546",
        collectiveInterventionArea=ALL_INTERVENTION_AREA,
        collectiveEmail="email@exemple.com",
        isPermanent=True,
    )
    landscape_image_path = pathlib.Path(generic_pictures.__path__[0]) / "landscape_01.jpg"
    offerers_api.save_venue_banner(
        user=user_offerer.user,
        venue=venue,
        content=landscape_image_path.read_bytes(),
        image_credit="industrial sandbox picture provider",
        image_alternative_text="Image de mon petit lieu",
    )
    offer_event = EventOfferFactory.create(
        name="Conférence gesticulée",
        venue=venue,
        subcategoryId=subcategories.CONFERENCE.id,
    )
    _create_tiny_works_and_artists(offer_event)
    stock = EventStockFactory.create(
        offer=offer_event,
        quantity=10,
        beginningDatetime=date_utils.get_naive_utc_now().replace(second=0, microsecond=0) + datetime.timedelta(days=20),
    )
    BookingFactory.create(quantity=1, stock=stock)
    _create_tiny_public_wishlists(venue)

    domain = db.session.query(educational_models.EducationalDomain).first()
    template = educational_factories.CollectiveOfferTemplateFactory.create(
        name="Conférence gesticulée",
        venue=venue,
        bookingEmails=[email],
        domains=[domain],
    )
    add_image_to_offer(template, "collective_offer_1.png")
    educational_institution = find_educational_institution_by_uai_code(UAI_FOR_FAKE_TOKEN)
    collective_offer = educational_factories.PublishedCollectiveOfferFactory(
        name="Ma petite offre réservable",
        venue=venue,
        domains=[domain],
        institution=educational_institution,
    )
    add_image_to_offer(
        collective_offer, "collective_offer_2.jpg", alternative_text="Image de ma petite offre réservable"
    )
    educational_factories.PlaylistFactory.create(
        distanceInKm=50,
        collective_offer_template=template,
        type=educational_models.PlaylistType.NEW_OFFER,
        institution=educational_institution,
    )
    educational_factories.PlaylistFactory.create(
        distanceInKm=50,
        collective_offer_template=template,
        type=educational_models.PlaylistType.NEW_OFFERER,
        institution=educational_institution,
        venue=venue,
    )

    logger.info("end create tiny venue with 1 booked offers, individual & collective")
