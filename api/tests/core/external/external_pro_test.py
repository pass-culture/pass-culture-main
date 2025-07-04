from dataclasses import asdict

import pytest

import pcapi.core.finance.factories as finance_factories
import pcapi.core.offerers.factories as offerers_factories
from pcapi.core.bookings.factories import BookingFactory
from pcapi.core.educational import factories as educational_factories
from pcapi.core.external.attributes.api import get_pro_attributes
from pcapi.core.finance.models import BankAccountApplicationStatus
from pcapi.core.offerers.models import VenueTypeCode
from pcapi.core.offers.factories import OfferFactory
from pcapi.core.offers.factories import StockFactory
from pcapi.core.offers.models import OfferValidationStatus
from pcapi.core.testing import assert_num_queries
from pcapi.core.users.factories import ProFactory
from pcapi.core.users.models import NotificationSubscriptions


pytestmark = pytest.mark.usefixtures("db_session")


# 1 query on user table with joinedload
# 1 query on venue table with joinedload
# 2 extra SQL queries: select exists on offer and booking tables
# 1 extra query to check if the venue has any related collective offer with 'marseille en grand'
# 1 check if the venue is concerned with marseille_en_grand
# 1 check if FF WIP_IS_OPEN_TO_PUBLIC is active
EXPECTED_PRO_ATTR_NUM_QUERIES = 7


def _build_params(subs, virt, perman, draft, accep, offer, book, attach, colloff, tploff, megoff):
    return pytest.param(
        subs,
        virt,
        perman,
        draft,
        accep,
        offer,
        book,
        attach,
        colloff,
        tploff,
        megoff,
        id=(
            f"sub:{subs}, vir:{virt}, per:{perman}, dra:{draft}, "
            f"acc:{accep}, off:{offer}, boo:{book}, "
            f"att:{attach}, colloff:{colloff}, tploff:{tploff}, megoff:{megoff}"
        ),
    )


@pytest.mark.parametrize(
    "enable_subscription,create_virtual,create_permanent,create_dms_draft,create_dms_accepted,"
    "create_individual_offer,create_booking,attached,create_collective_offer,create_template_offer,create_collective_offer_meg",
    [
        #             subs, virt, perman, draft, accep, offer, book, attach, colloff, tploff, megoff
        _build_params(False, False, False, False, False, False, False, "none", False, False, False),
        _build_params(True, False, True, True, False, True, False, "one", True, False, False),
        _build_params(False, True, False, False, True, True, False, "all", False, True, False),
        _build_params(True, True, True, True, True, True, True, "none", True, True, False),
        _build_params(False, True, True, False, True, False, False, "one", True, False, False),
        _build_params(True, True, True, True, True, True, True, "all", True, True, False),
        _build_params(False, False, False, False, False, False, False, "none", True, False, True),
    ],
)
def test_update_external_pro_user_attributes(
    enable_subscription,
    create_virtual,
    create_permanent,
    create_dms_draft,
    create_dms_accepted,
    create_individual_offer,
    create_booking,
    attached,
    create_collective_offer,
    create_template_offer,
    create_collective_offer_meg,
):
    email = "juste.leblanc@example.net"

    pro_user = ProFactory(
        firstName="Juste",
        lastName="Leblanc",
        email=email,
        notificationSubscriptions=asdict(NotificationSubscriptions(marketing_email=enable_subscription)),
    )

    venue_label_a = offerers_factories.VenueLabelFactory(label="Cinéma d'art et d'essai")
    venue_label_b = offerers_factories.VenueLabelFactory(label="Scènes conventionnées")

    offerer1 = offerers_factories.OffererFactory(
        siren="111222333",
        name="Plage Culture",
        tags=[offerers_factories.OffererTagFactory(name="top-acteur", label="Top Acteur")],
    )
    if attached in ("one", "all"):
        offerers_factories.UserOffererFactory(user=ProFactory(), offerer=offerer1)
    offerers_factories.UserOffererFactory(user=pro_user, offerer=offerer1)

    collective_offers = []
    if create_collective_offer:
        if create_collective_offer_meg:
            program = educational_factories.EducationalInstitutionProgramFactory(name="marseille_en_grand")
            institution = educational_factories.EducationalInstitutionFactory(
                programAssociations=[
                    educational_factories.EducationalInstitutionProgramAssociationFactory(
                        program=program,
                    )
                ]
            )

            collective_offer = educational_factories.CollectiveOfferFactory(isActive=True, institution=institution)
        else:
            collective_offer = educational_factories.CollectiveOfferFactory(isActive=True)

        collective_offers.append(collective_offer)

    venue1 = offerers_factories.VenueFactory(
        managingOfferer=offerer1,
        name="Cinéma de la plage",
        offererAddress__address__street="Rue des étoiles",
        offererAddress__address__departmentCode="06",
        offererAddress__address__postalCode="06590",
        offererAddress__address__city="Théoule-sur-mer",
        bookingEmail=email,
        siret="11122233300001",
        isPermanent=create_permanent,
        venueTypeCode=VenueTypeCode.MOVIE,
        venueLabelId=venue_label_a.id,
        adageId="12345" if create_collective_offer else None,
        collectiveOffers=collective_offers,
        collectiveOfferTemplates=(
            [educational_factories.CollectiveOfferTemplateFactory(isActive=True)] if create_template_offer else []
        ),
    )
    venue1b = offerers_factories.VenueFactory(
        managingOfferer=offerer1,
        name="Théâtre de la plage",
        offererAddress__address__street="Rue des molières",
        offererAddress__address__departmentCode="06",
        offererAddress__address__postalCode="06590",
        offererAddress__address__city="Théoule-sur-mer",
        bookingEmail=email,
        siret="11122233300002",
        isPermanent=create_permanent,
        venueTypeCode=VenueTypeCode.PERFORMING_ARTS,
        venueLabelId=venue_label_b.id,
    )

    if create_dms_accepted:
        offerers_factories.VenueBankAccountLinkFactory(
            venue=venue1, bankAccount=finance_factories.BankAccountFactory(status=BankAccountApplicationStatus.ACCEPTED)
        )
        offerers_factories.VenueBankAccountLinkFactory(
            venue=venue1b,
            bankAccount=finance_factories.BankAccountFactory(status=BankAccountApplicationStatus.ACCEPTED),
        )

    if create_virtual:
        offerer2 = offerers_factories.OffererFactory(siren="444555666", name="Culture en ligne")
        if attached == "all":
            offerers_factories.UserOffererFactory(user=ProFactory(), offerer=offerer2)
        offerers_factories.UserOffererFactory(user=pro_user, offerer=offerer2)
        venue2 = offerers_factories.VirtualVenueFactory(
            managingOfferer=offerer2,
            name="Théâtre en ligne",
            bookingEmail=email,
            isPermanent=create_permanent,
            venueTypeCode=VenueTypeCode.DIGITAL,
            venueLabelId=None,
        )

        if create_dms_accepted:
            offerers_factories.VenueBankAccountLinkFactory(
                venue=venue2,
                bankAccount=finance_factories.BankAccountFactory(status=BankAccountApplicationStatus.ACCEPTED),
            )

    # Offerer not linked to user email but with the same booking email
    offerer3 = offerers_factories.OffererFactory(
        siren="777899888",
        name="Plage Events",
        tags=[offerers_factories.OffererTagFactory(name="collectivite", label="Collectivité")],
    )
    venue3 = offerers_factories.VenueFactory(
        managingOfferer=offerer3,
        name="Festival de la mer",
        offererAddress__address__street="Promenade de l'ire landaise",
        offererAddress__address__departmentCode="83",
        offererAddress__address__postalCode="83700",
        offererAddress__address__city="Saint-Raphaël",
        bookingEmail=email,
        siret="77789988800001",
        isPermanent=False,
        venueTypeCode=VenueTypeCode.PERFORMING_ARTS,
        venueLabelId=None,
    )

    if create_individual_offer:
        offer1 = OfferFactory(validation=OfferValidationStatus.APPROVED, isActive=True, venue=venue3)
        stock1 = StockFactory(offer=offer1)
        offer2 = OfferFactory(validation=OfferValidationStatus.APPROVED, isActive=True, venue=venue3)
        StockFactory(offer=offer2)
        if create_booking:
            for _ in range(5):
                BookingFactory(stock=stock1)

    if create_dms_draft:
        offerers_factories.VenueBankAccountLinkFactory(
            venue=venue3, bankAccount=finance_factories.BankAccountFactory(status=BankAccountApplicationStatus.DRAFT)
        )
    elif create_dms_accepted:
        offerers_factories.VenueBankAccountLinkFactory(
            venue=venue3, bankAccount=finance_factories.BankAccountFactory(status=BankAccountApplicationStatus.ACCEPTED)
        )
    # This offerer is managed by pro user but venue has a different email address
    offerer4 = offerers_factories.OffererFactory(siren="001002003", name="Juste Libraire")
    if attached == "all":
        offerers_factories.UserOffererFactory(user=ProFactory(), offerer=offerer4)
    offerers_factories.UserOffererFactory(user=pro_user, offerer=offerer4)
    venue4 = offerers_factories.VenueFactory(
        managingOfferer=offerer4,
        name="Librairie du port",
        offererAddress__address__street="Rue du phare à éon",
        offererAddress__address__departmentCode="13",
        offererAddress__address__postalCode="13260",
        offererAddress__address__city="Cassis",
        bookingEmail="librairie@example.net",
        siret="00100200300001",
        isPermanent=create_permanent,
        venueTypeCode=VenueTypeCode.BOOKSTORE,
        venueLabelId=None,
    )

    # Offerer and venue should be ignored when building attributes: not yet validated
    offerers_factories.VenueFactory(
        managingOfferer=offerers_factories.UserNotValidatedOffererFactory(user=pro_user).offerer, bookingEmail=email
    )

    if create_dms_accepted:
        offerers_factories.VenueBankAccountLinkFactory(
            venue=venue4, bankAccount=finance_factories.BankAccountFactory(status=BankAccountApplicationStatus.ACCEPTED)
        )
    else:
        # Bank accounts which do not make ds attributes return True: on offerer, on venue with other email, refused
        finance_factories.BankAccountFactory(offerer=offerer1, status=BankAccountApplicationStatus.ACCEPTED)
        offerers_factories.VenueBankAccountLinkFactory(
            venue=venue4, bankAccount=finance_factories.BankAccountFactory(status=BankAccountApplicationStatus.ACCEPTED)
        )
        offerers_factories.VenueBankAccountLinkFactory(
            venue=venue1, bankAccount=finance_factories.BankAccountFactory(status=BankAccountApplicationStatus.REFUSED)
        )

    # Create inactive offerer and its venue, linked to email, which should not be taken into account in any attribute
    inactive_offerer = offerers_factories.OffererFactory(
        siren="999999999",
        name="Structure désactivée",
        isActive=False,
        tags=[offerers_factories.OffererTagFactory(name="desactive", label="Désactivé")],
    )
    offerers_factories.UserOffererFactory(user=pro_user, offerer=inactive_offerer)
    offerers_factories.VenueFactory(
        managingOfferer=inactive_offerer,
        name="Salle de concert des calanques",
        offererAddress__address__street="Rue des myrtilles",
        offererAddress__address__departmentCode="13",  # different from others
        offererAddress__address__postalCode="13260",
        offererAddress__address__city="Cassis",
        bookingEmail=email,
        siret="99999999900009",
        isPermanent=create_permanent,
        venueTypeCode=VenueTypeCode.CONCERT_HALL,  # different from others
    )

    num_queries = EXPECTED_PRO_ATTR_NUM_QUERIES
    if create_booking:
        num_queries -= 1  # feature flags are already cached by BeneficiaryGrant18Factory.beneficiaryImports

    with assert_num_queries(num_queries):
        attributes = get_pro_attributes(email)

    assert attributes.is_pro is True
    assert attributes.is_active_pro is True
    assert attributes.is_user_email is True
    assert attributes.is_booking_email is True
    assert attributes.marketing_email_subscription is enable_subscription
    assert (
        attributes.offerers_names == {"Culture en ligne", "Juste Libraire", "Plage Culture", "Plage Events"}
        if create_virtual
        else {"Juste Libraire", "Plage Culture", "Plage Events"}
    )
    assert attributes.offerers_tags == {"top-acteur", "collectivite"}
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
    assert attributes.isOpenToPublic is create_permanent
    assert attributes.has_individual_offers is create_individual_offer
    assert attributes.has_bookings is create_booking
    assert attributes.has_collective_offers == (create_collective_offer or create_template_offer)
    assert attributes.has_offers == (create_individual_offer or create_collective_offer or create_template_offer)
    assert attributes.is_eac_meg == create_collective_offer_meg


def test_update_external_pro_user_attributes_no_offerer_no_venue():
    user = ProFactory()

    _check_user_without_validated_offerer(user)


@pytest.mark.parametrize(
    "offerer_factory", [offerers_factories.NewOffererFactory, offerers_factories.ClosedOffererFactory]
)
def test_update_external_non_attached_pro_user_attributes(offerer_factory):
    user_offerer = offerers_factories.UserNotValidatedOffererFactory(offerer=offerer_factory())
    offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer, bookingEmail=user_offerer.user.email)

    _check_user_without_validated_offerer(user_offerer.user)


def _check_user_without_validated_offerer(user):
    email = user.email

    # no booking or offer to check without offerer
    # only 2 queries: user and venue
    with assert_num_queries(2):
        attributes = get_pro_attributes(email)

    assert attributes.is_pro is True
    assert attributes.is_active_pro is False
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
    assert attributes.isOpenToPublic is None
    assert attributes.has_offers is None
    assert attributes.has_bookings is None
    assert attributes.has_collective_offers is False


def test_update_external_pro_booking_email_attributes():
    email = "musee@example.net"
    offerer = offerers_factories.OffererFactory(siren="123456789", name="Musée")
    venue = offerers_factories.VenueFactory(
        managingOfferer=offerer,
        name="Musée de la châtaigne",
        offererAddress__address__departmentCode="06",
        offererAddress__address__postalCode="06420",
        bookingEmail=email,
        siret="12345678900001",
        isPermanent=True,
        isOpenToPublic=True,
        venueTypeCode=VenueTypeCode.MUSEUM,
    )

    with assert_num_queries(EXPECTED_PRO_ATTR_NUM_QUERIES):
        attributes = get_pro_attributes(email)

    assert attributes.is_pro is True
    assert attributes.is_active_pro is True
    assert attributes.is_user_email is False
    assert attributes.is_booking_email is True
    assert attributes.marketing_email_subscription is True
    assert attributes.offerers_names == {offerer.name}
    assert attributes.venues_ids == {venue.id}
    assert attributes.venues_names == {venue.name}
    assert attributes.venues_types == {venue.venueTypeCode.name}
    assert attributes.venues_labels == set()
    assert attributes.departement_code == {venue.offererAddress.address.departmentCode}
    assert attributes.postal_code == {venue.offererAddress.address.postalCode}

    assert attributes.user_id is None
    assert attributes.first_name is None
    assert attributes.last_name is None
    assert attributes.user_is_attached is None
    assert attributes.user_is_creator is None

    assert attributes.dms_application_submitted is False
    assert attributes.dms_application_approved is False
    assert attributes.isVirtual is False
    assert attributes.isPermanent is True
    assert attributes.isOpenToPublic is True
    assert attributes.has_banner_url is False
    assert attributes.has_offers is False
    assert attributes.has_bookings is False


def test_update_external_pro_booking_email_attributes_for_permanent_venue_with_banner():
    email = "musee@example.net"
    offerer = offerers_factories.OffererFactory(siren="123456789", name="Musée")
    offerers_factories.VenueFactory(
        managingOfferer=offerer,
        name="Musée de la châtaigne",
        offererAddress__address__departmentCode="06",
        offererAddress__address__postalCode="06420",
        bookingEmail=email,
        siret="12345678900001",
        isPermanent=True,
        venueTypeCode=VenueTypeCode.MUSEUM,
        _bannerUrl="https://example.net/banner.jpg",
    )

    with assert_num_queries(EXPECTED_PRO_ATTR_NUM_QUERIES):
        attributes = get_pro_attributes(email)
    assert attributes.isPermanent is True
    assert attributes.has_banner_url is True


def test_update_external_pro_booking_email_attributes_for_non_permanent_venue_with_banner():
    email = "musee@example.net"
    offerer = offerers_factories.OffererFactory(siren="123456789", name="Musée")
    offerers_factories.VenueFactory(
        managingOfferer=offerer,
        name="Musée de la châtaigne",
        offererAddress__address__departmentCode="06",
        offererAddress__address__postalCode="06420",
        bookingEmail=email,
        siret="12345678900001",
        isPermanent=False,
        venueTypeCode=VenueTypeCode.MUSEUM,
        _bannerUrl="https://example.net/banner.jpg",
    )

    with assert_num_queries(EXPECTED_PRO_ATTR_NUM_QUERIES):
        attributes = get_pro_attributes(email)
    assert attributes.isPermanent is False
    assert attributes.has_banner_url is True


def test_update_external_pro_booking_email_attributes_for_non_permanent_venue_without_banner():
    email = "musee@example.net"
    offerer = offerers_factories.OffererFactory(siren="123456789", name="Musée")
    offerers_factories.VenueFactory(
        managingOfferer=offerer,
        name="Musée de la châtaigne",
        offererAddress__address__departmentCode="06",
        offererAddress__address__postalCode="06420",
        bookingEmail=email,
        siret="12345678900001",
        isPermanent=False,
        venueTypeCode=VenueTypeCode.MUSEUM,
    )

    with assert_num_queries(EXPECTED_PRO_ATTR_NUM_QUERIES):
        attributes = get_pro_attributes(email)
    assert attributes.isPermanent is False
    assert attributes.has_banner_url is True


def test_update_external_pro_removed_email_attributes():
    _check_no_matching_email("removed@example.net")


def test_update_external_pro_booking_email_closed_offerer():
    venue = offerers_factories.VenueFactory(managingOfferer=offerers_factories.ClosedOffererFactory())
    _check_no_matching_email(venue.bookingEmail)


def _check_no_matching_email(email):
    # only 2 queries: user and venue - nothing found
    with assert_num_queries(2):
        attributes = get_pro_attributes(email)

    assert attributes.is_pro is True
    assert attributes.is_active_pro is False
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
    assert attributes.isOpenToPublic is None
    assert attributes.has_offers is None
    assert attributes.has_bookings is None
