from dataclasses import asdict

import pytest

from pcapi.core.bookings.factories import BookingFactory
import pcapi.core.finance.factories as finance_factories
from pcapi.core.finance.models import BankInformationStatus
import pcapi.core.offerers.factories as offerers_factories
from pcapi.core.offerers.models import VenueTypeCode
from pcapi.core.offers.factories import OfferFactory
from pcapi.core.offers.factories import StockFactory
from pcapi.core.offers.models import OfferValidationStatus
from pcapi.core.users.external import get_pro_attributes
from pcapi.core.users.factories import ProFactory
from pcapi.core.users.models import NotificationSubscriptions


pytestmark = pytest.mark.usefixtures("db_session")


def _build_params(subs, virt, perman, draft, accep, offer, book, attach):
    return pytest.param(
        subs,
        virt,
        perman,
        draft,
        accep,
        offer,
        book,
        attach,
        id=f"sub:{subs}, vir:{virt}, per:{perman}, dra:{draft}, " f"acc:{accep}, off:{offer}, boo:{book}, att:{attach}",
    )


@pytest.mark.parametrize(
    "enable_subscription,create_virtual,create_permanent,create_dms_draft,create_dms_accepted,"
    "create_offer,create_booking,attached",
    [
        #             subs, virt, perman, draft, accep, offer, book, attach
        _build_params(False, False, False, False, False, False, False, "none"),
        _build_params(True, False, True, True, False, True, False, "one"),
        _build_params(False, True, False, False, True, True, False, "all"),
        _build_params(True, True, True, True, True, True, True, "none"),
        _build_params(False, True, True, False, True, False, False, "one"),
        _build_params(True, True, True, True, True, True, True, "all"),
    ],
)
def test_update_external_pro_user_attributes(
    enable_subscription,
    create_virtual,
    create_permanent,
    create_dms_draft,
    create_dms_accepted,
    create_offer,
    create_booking,
    attached,
):
    email = "juste.leblanc@example.net"

    pro_user = ProFactory(
        publicName="Juste Leblanc",
        firstName="Juste",
        lastName="Leblanc",
        email=email,
        notificationSubscriptions=asdict(NotificationSubscriptions(marketing_email=enable_subscription)),
    )

    venue_label_a = offerers_factories.VenueLabelFactory(label="Cinéma d'art et d'essai")
    venue_label_b = offerers_factories.VenueLabelFactory(label="Scènes conventionnées")

    offerer1 = offerers_factories.OffererFactory(siren="111222333", name="Plage Culture")
    if attached in ("one", "all"):
        offerers_factories.UserOffererFactory(user=ProFactory(), offerer=offerer1)
    offerers_factories.UserOffererFactory(user=pro_user, offerer=offerer1)
    venue1 = offerers_factories.VenueFactory(
        managingOfferer=offerer1,
        name="Cinéma de la plage",
        departementCode="06",
        postalCode="06590",
        city="Théoule-sur-mer",
        bookingEmail=email,
        siret="11122233300001",
        isPermanent=create_permanent,
        venueTypeCode=VenueTypeCode.MOVIE,
        venueLabelId=venue_label_a.id,
    )
    venue1b = offerers_factories.VenueFactory(
        managingOfferer=offerer1,
        name="Théâtre de la plage",
        departementCode="06",
        postalCode="06590",
        city="Théoule-sur-mer",
        bookingEmail=email,
        siret="11122233300002",
        isPermanent=create_permanent,
        venueTypeCode=VenueTypeCode.PERFORMING_ARTS,
        venueLabelId=venue_label_b.id,
    )

    if create_dms_accepted:
        finance_factories.BankInformationFactory(venue=venue1, status=BankInformationStatus.ACCEPTED)
        finance_factories.BankInformationFactory(venue=venue1b, status=BankInformationStatus.ACCEPTED)

    if create_virtual:
        offerer2 = offerers_factories.OffererFactory(siren="444555666", name="Culture en ligne")
        if attached == "all":
            offerers_factories.UserOffererFactory(user=ProFactory(), offerer=offerer2)
        offerers_factories.UserOffererFactory(user=pro_user, offerer=offerer2)
        venue2 = offerers_factories.VenueFactory(
            managingOfferer=offerer2,
            name="Théâtre en ligne",
            departementCode=None,
            postalCode=None,
            city=None,
            bookingEmail=email,
            siret=None,
            isPermanent=create_permanent,
            isVirtual=True,
            venueTypeCode=VenueTypeCode.DIGITAL,
            venueLabelId=None,
        )

        if create_dms_accepted:
            finance_factories.BankInformationFactory(venue=venue2, status=BankInformationStatus.ACCEPTED)

    # Offerer not linked to user email but with the same booking email
    offerer3 = offerers_factories.OffererFactory(siren="777888999", name="Plage Events")
    venue3 = offerers_factories.VenueFactory(
        managingOfferer=offerer3,
        name="Festival de la mer",
        departementCode="83",
        postalCode="83700",
        city="Saint-Raphaël",
        bookingEmail=email,
        siret="77788899900001",
        isPermanent=False,
        venueTypeCode=VenueTypeCode.PERFORMING_ARTS,
        venueLabelId=None,
    )

    if create_offer:
        offer1 = OfferFactory(validation=OfferValidationStatus.APPROVED, isActive=True, venue=venue3)
        stock1 = StockFactory(offer=offer1)
        offer2 = OfferFactory(validation=OfferValidationStatus.APPROVED, isActive=True, venue=venue3)
        StockFactory(offer=offer2)
        if create_booking:
            for _ in range(5):
                BookingFactory(stock=stock1)

    if create_dms_draft:
        finance_factories.BankInformationFactory(venue=venue3, status=BankInformationStatus.DRAFT)
    elif create_dms_accepted:
        finance_factories.BankInformationFactory(venue=venue3, status=BankInformationStatus.ACCEPTED)

    # This offerer is managed by pro user but venue has a different email address
    offerer4 = offerers_factories.OffererFactory(siren="001002003", name="Juste Libraire")
    if attached == "all":
        offerers_factories.UserOffererFactory(user=ProFactory(), offerer=offerer4)
    offerers_factories.UserOffererFactory(user=pro_user, offerer=offerer4)
    venue4 = offerers_factories.VenueFactory(
        managingOfferer=offerer4,
        name="Librairie du port",
        departementCode="13",
        postalCode="13260",
        city="Cassis",
        bookingEmail="librairie@example.net",
        siret="00100200300001",
        isPermanent=create_permanent,
        venueTypeCode=VenueTypeCode.BOOKSTORE,
        venueLabelId=None,
    )

    if create_dms_accepted:
        finance_factories.BankInformationFactory(venue=venue4, status=BankInformationStatus.ACCEPTED)
    else:
        # Bank information which do not make dms attributes return True: on offerer, on venue with other email, rejected
        finance_factories.BankInformationFactory(offerer=offerer1, status=BankInformationStatus.ACCEPTED)
        finance_factories.BankInformationFactory(venue=venue4, status=BankInformationStatus.ACCEPTED)
        finance_factories.BankInformationFactory(venue=venue1, status=BankInformationStatus.REJECTED)

    # Create inactive offerer and its venue, linked to email, which should not be taken into account in any attribute
    inactive_offerer = offerers_factories.OffererFactory(siren="999999999", name="Structure désactivée", isActive=False)
    offerers_factories.UserOffererFactory(user=pro_user, offerer=inactive_offerer)
    offerers_factories.VenueFactory(
        managingOfferer=inactive_offerer,
        name="Salle de concert des calanques",
        departementCode="13",  # different from others
        postalCode="13260",
        city="Cassis",
        bookingEmail=email,
        siret="99999999900009",
        isPermanent=create_permanent,
        venueTypeCode=VenueTypeCode.CONCERT_HALL,  # different from others
    )

    attributes = get_pro_attributes(pro_user.email)

    assert attributes.is_pro is True
    assert attributes.is_user_email is True
    assert attributes.is_booking_email is True
    assert attributes.marketing_email_subscription is enable_subscription
    assert (
        attributes.offerers_names == {"Culture en ligne", "Juste Libraire", "Plage Culture", "Plage Events"}
        if create_virtual
        else {"Juste Libraire", "Plage Culture", "Plage Events"}
    )
    assert len(attributes.venues_ids) == 5 if create_virtual else 4
    assert (
        attributes.venues_names
        == {"Cinéma de la plage", "Festival de la mer", "Théâtre de la plage", "Théâtre en ligne", "Librairie du port"}
        if create_virtual
        else {"Cinéma de la plage", "Festival de la mer", "Théâtre de la plage", "Librairie du port"}
    )
    assert (
        attributes.venues_types
        == {
            VenueTypeCode.DIGITAL.name,
            VenueTypeCode.MOVIE.name,
            VenueTypeCode.PERFORMING_ARTS.name,
            VenueTypeCode.BOOKSTORE.name,
        }
        if create_virtual
        else {VenueTypeCode.MOVIE.name, VenueTypeCode.PERFORMING_ARTS.name, VenueTypeCode.BOOKSTORE.name}
    )
    assert attributes.venues_labels == {"Cinéma d'art et d'essai", "Scènes conventionnées"}
    assert attributes.departement_code == {"06", "83", "13"}
    assert attributes.postal_code == {"06590", "83700", "13260"}

    assert attributes.user_id == pro_user.id
    assert attributes.first_name == pro_user.firstName
    assert attributes.last_name == pro_user.lastName
    assert attributes.user_is_attached is (attached in ("one", "all"))
    assert attributes.user_is_creator is not (attached == "all")

    assert attributes.dms_application_submitted is create_dms_draft
    assert attributes.dms_application_approved is (create_dms_accepted and not create_dms_draft)
    assert attributes.isVirtual is create_virtual
    assert attributes.isPermanent is create_permanent
    assert attributes.has_offers is create_offer
    assert attributes.has_bookings is create_booking


def test_update_external_pro_user_attributes_no_offerer_no_venue():
    user = ProFactory()

    attributes = get_pro_attributes(user.email)

    assert attributes.is_pro is True
    assert attributes.is_user_email is True
    assert attributes.is_booking_email is False
    assert attributes.marketing_email_subscription is True
    assert attributes.offerers_names == set()
    assert attributes.venues_ids == set()
    assert attributes.venues_names == set()
    assert attributes.venues_types == set()
    assert attributes.venues_labels == set()
    assert attributes.departement_code == set()
    assert attributes.postal_code == set()

    assert attributes.user_id == user.id
    assert attributes.first_name == user.firstName
    assert attributes.last_name == user.lastName
    assert attributes.user_is_attached is False
    assert attributes.user_is_creator is False

    assert attributes.dms_application_submitted is None
    assert attributes.dms_application_approved is None
    assert attributes.isVirtual is None
    assert attributes.isPermanent is None
    assert attributes.has_offers is None
    assert attributes.has_bookings is None


def test_update_external_pro_booking_email_attributes():
    email = "musee@example.net"
    offerer = offerers_factories.OffererFactory(siren="123456789", name="Musée")
    venue = offerers_factories.VenueFactory(
        managingOfferer=offerer,
        name="Musée de la châtaigne",
        departementCode="06",
        postalCode="06420",
        bookingEmail=email,
        siret="12345678900001",
        isPermanent=True,
        venueTypeCode=VenueTypeCode.MUSEUM,
    )

    attributes = get_pro_attributes(email)

    assert attributes.is_pro is True
    assert attributes.is_user_email is False
    assert attributes.is_booking_email is True
    assert attributes.marketing_email_subscription is True
    assert attributes.offerers_names == {offerer.name}
    assert attributes.venues_ids == {venue.id}
    assert attributes.venues_names == {venue.name}
    assert attributes.venues_types == {venue.venueTypeCode.name}
    assert attributes.venues_labels == set()
    assert attributes.departement_code == {venue.departementCode}
    assert attributes.postal_code == {venue.postalCode}

    assert attributes.user_id is None
    assert attributes.first_name is None
    assert attributes.last_name is None
    assert attributes.user_is_attached is None
    assert attributes.user_is_creator is None

    assert attributes.dms_application_submitted is False
    assert attributes.dms_application_approved is False
    assert attributes.isVirtual is False
    assert attributes.isPermanent is True
    assert attributes.has_offers is False
    assert attributes.has_bookings is False


def test_update_external_pro_removed_email_attributes():
    attributes = get_pro_attributes("removed@example.net")

    assert attributes.is_pro is True
    assert attributes.is_user_email is False
    assert attributes.is_booking_email is False
    assert attributes.marketing_email_subscription is False
    assert attributes.offerers_names == set()
    assert attributes.venues_ids == set()
    assert attributes.venues_names == set()
    assert attributes.venues_types == set()
    assert attributes.venues_labels == set()
    assert attributes.departement_code == set()
    assert attributes.postal_code == set()

    assert attributes.user_id is None
    assert attributes.first_name is None
    assert attributes.last_name is None
    assert attributes.user_is_attached is None
    assert attributes.user_is_creator is None

    assert attributes.dms_application_submitted is None
    assert attributes.dms_application_approved is None
    assert attributes.isVirtual is None
    assert attributes.isPermanent is None
    assert attributes.has_offers is None
    assert attributes.has_bookings is None
