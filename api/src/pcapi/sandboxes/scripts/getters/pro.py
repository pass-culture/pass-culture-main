import datetime

from pcapi.core.bookings import models as bookings_models
import pcapi.core.bookings.factories as bookings_factories
from pcapi.core.categories import subcategories
from pcapi.core.categories.models import EacFormat
import pcapi.core.educational.factories as educational_factories
import pcapi.core.educational.models as educational_models
from pcapi.core.educational.utils import UAI_FOR_FAKE_TOKEN
from pcapi.core.finance import factories as finance_factories
from pcapi.core.offerers import api as offerers_api
import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offers.factories as offers_factories
from pcapi.core.providers import factories as providers_factories
from pcapi.core.users import factories as users_factories
from pcapi.models import db
from pcapi.sandboxes.scripts.utils.helpers import get_pro_user_helper


def create_new_pro_user() -> dict:
    pro_user = users_factories.ProFactory.create()
    return {"user": get_pro_user_helper(pro_user)}


def create_new_pro_user_and_offerer() -> dict:
    pro_user = users_factories.ProFactory.create()
    offerer = offerers_factories.OffererFactory.create()
    offerers_factories.VirtualVenueFactory.create(managingOfferer=offerer)
    return {"user": get_pro_user_helper(pro_user), "siren": offerer.siren}


def create_new_pro_user_and_offerer_with_venue() -> dict:
    pro_user = users_factories.ProFactory.create()
    offerer = offerers_factories.OffererFactory.create()
    venue = offerers_factories.VenueFactory.create(managingOfferer=offerer, isPermanent=True)
    offerers_factories.VirtualVenueFactory.create(managingOfferer=offerer)
    return {"user": get_pro_user_helper(pro_user), "siret": venue.siret}


def create_regular_pro_user() -> dict:
    pro_user = users_factories.ProFactory.create()
    offerer = offerers_factories.OffererFactory.create()
    offerers_factories.UserOffererFactory.create(user=pro_user, offerer=offerer)
    venue = offerers_factories.VenueFactory.create(name="Mon Lieu", managingOfferer=offerer, isPermanent=True)
    offerers_factories.VirtualVenueFactory.create(managingOfferer=offerer)
    offerers_factories.VenueLabelFactory.create(label="Musée de France")

    return {"user": get_pro_user_helper(pro_user), "siren": offerer.siren, "venueName": venue.name}


def create_regular_pro_user_already_onboarded() -> dict:
    pro_user = users_factories.ProFactory.create()
    offerer = offerers_factories.OffererFactory.create()
    offerers_factories.UserOffererFactory.create(user=pro_user, offerer=offerer)
    venue = offerers_factories.VenueFactory.create(
        name="Mon Lieu", managingOfferer=offerer, isPermanent=True, adageId="1337"
    )  # Adding an adageId will make this user onboarded
    offerers_factories.VirtualVenueFactory.create(managingOfferer=offerer)
    offerers_factories.VenueLabelFactory.create(label="Musée de France")

    return {"user": get_pro_user_helper(pro_user), "siren": offerer.siren, "venueName": venue.name}


def create_pro_user_with_bookings() -> dict:
    pro_user = users_factories.ProFactory.create()
    offerer = offerers_factories.OffererFactory.create()
    offerers_factories.UserOffererFactory.create(user=pro_user, offerer=offerer)
    venue = offerers_factories.VenueFactory.create(name="Mon Lieu", managingOfferer=offerer, isPermanent=True)
    offerers_factories.VirtualVenueFactory.create(managingOfferer=offerer)
    stock = offers_factories.StockFactory.create(offer__venue=venue)
    stock_event = offers_factories.EventStockFactory.create(offer__venue=venue)

    booking_confirmed = bookings_factories.BookingFactory.create(
        token="2XTM3W", stock=stock, status=bookings_models.BookingStatus.CONFIRMED
    )
    booking_too_soon = bookings_factories.BookingFactory.create(
        token="TOSOON", stock=stock_event, status=bookings_models.BookingStatus.CONFIRMED
    )
    booking_used = bookings_factories.BookingFactory.create(
        token="XUSEDX", stock=stock, status=bookings_models.BookingStatus.USED
    )
    booking_canceled = bookings_factories.BookingFactory.create(
        token="CANCEL", stock=stock, status=bookings_models.BookingStatus.CANCELLED
    )
    booking_reimbursed = bookings_factories.BookingFactory.create(
        token="REIMBU", stock=stock, status=bookings_models.BookingStatus.REIMBURSED
    )
    booking_other_x = bookings_factories.BookingFactory.create(token="OTHERX")
    return {
        "user": get_pro_user_helper(pro_user),
        "tokenConfirmed": booking_confirmed.token,
        "tokenTooSoon": booking_too_soon.token,
        "tokenUsed": booking_used.token,
        "tokenCanceled": booking_canceled.token,
        "tokenReimbursed": booking_reimbursed.token,
        "tokenOther": booking_other_x.token,
    }


def create_regular_pro_user_with_virtual_offer() -> dict:
    pro_user = users_factories.ProFactory.create()
    offerer = offerers_factories.OffererFactory.create()
    offerers_factories.UserOffererFactory.create(user=pro_user, offerer=offerer)
    offerers_factories.VenueFactory.create(name="Mon Lieu", managingOfferer=offerer, isPermanent=True)
    virtual_venue = offerers_factories.VirtualVenueFactory.create(managingOfferer=offerer)
    offers_factories.OfferFactory.create(
        name="Mon offre virtuelle",
        subcategoryId=subcategories.ABO_PLATEFORME_VIDEO.id,
        venue=virtual_venue,
        url="http://www.example.com",
    )
    return {"user": get_pro_user_helper(pro_user)}


def create_pro_user_with_financial_data() -> dict:
    pro_user = users_factories.ProFactory.create()
    offerer_A = offerers_factories.OffererFactory.create()
    offerers_factories.UserOffererFactory.create(user=pro_user, offerer=offerer_A)
    offerers_factories.VenueFactory.create(name="Mon Lieu", managingOfferer=offerer_A)
    offerers_factories.VirtualVenueFactory.create(managingOfferer=offerer_A)

    offerer_B = offerers_factories.OffererFactory.create(name="Structure avec informations bancaires")
    offerers_factories.UserOffererFactory.create(user=pro_user, offerer=offerer_B)
    venue_B = offerers_factories.VenueFactory.create(name="Mon Lieu", managingOfferer=offerer_B)
    offerers_factories.VirtualVenueFactory.create(managingOfferer=offerer_B)
    bank_account_B = finance_factories.BankAccountFactory.create(offerer=offerer_B)
    offerers_factories.VenuePricingPointLinkFactory.create(
        venue=venue_B,
        pricingPoint=venue_B,
    )
    finance_factories.InvoiceFactory.create(bankAccount=bank_account_B)

    return {"user": get_pro_user_helper(pro_user)}


def create_pro_user_with_financial_data_and_3_venues() -> dict:
    pro_user = users_factories.ProFactory.create()

    offerer_C = offerers_factories.OffererFactory.create(name="Structure avec informations bancaires et 3 lieux")
    offerers_factories.UserOffererFactory.create(user=pro_user, offerer=offerer_C)
    venue_C = offerers_factories.VenueFactory.create(name="Mon lieu 1", managingOfferer=offerer_C)
    venue_D = offerers_factories.VenueFactory.create(name="Mon lieu 2", managingOfferer=offerer_C)
    venue_E = offerers_factories.VenueFactory.create(name="Mon lieu 3", managingOfferer=offerer_C)
    offerers_factories.VirtualVenueFactory.create(managingOfferer=offerer_C)
    bank_account_C = finance_factories.BankAccountFactory.create(offerer=offerer_C)
    offerers_factories.VenuePricingPointLinkFactory.create(
        venue=venue_C,
        pricingPoint=venue_C,
    )
    offerers_factories.VenuePricingPointLinkFactory.create(
        venue=venue_D,
        pricingPoint=venue_D,
    )
    offerers_factories.VenuePricingPointLinkFactory.create(
        venue=venue_E,
        pricingPoint=venue_E,
    )
    finance_factories.InvoiceFactory.create(bankAccount=bank_account_C)
    finance_factories.InvoiceFactory.create(bankAccount=bank_account_C)
    finance_factories.InvoiceFactory.create(bankAccount=bank_account_C)

    return {"user": get_pro_user_helper(pro_user)}


def create_adage_environment() -> dict:
    current_year = educational_factories.EducationalCurrentYearFactory.create()
    next_year = educational_factories.EducationalYearFactory.create()

    offer = educational_factories.CollectiveOfferTemplateFactory.create(name="Mon offre collective")

    educational_institution = educational_factories.EducationalInstitutionFactory.create(
        # should match id of user generated in create_adage_jwt_fake_token
        institutionId=UAI_FOR_FAKE_TOKEN,
    )
    educational_factories.PlaylistFactory.create(
        distanceInKm=50,
        collective_offer_template=offer,
        type=educational_models.PlaylistType.NEW_OFFER,
        institution=educational_institution,
    )
    newOfferer = educational_factories.PlaylistFactory.create(
        distanceInKm=50,
        collective_offer_template=offer,
        type=educational_models.PlaylistType.NEW_OFFERER,
        institution=educational_institution,
        venue__name="Mon lieu collectif",
    )
    educational_factories.EducationalDepositFactory.create(
        educationalInstitution=educational_institution,
        educationalYear=current_year,
        amount=40000,
    )
    educational_factories.EducationalDepositFactory.create(
        educationalInstitution=educational_institution,
        educationalYear=next_year,
        amount=50000,
        isFinal=False,
    )

    # offer result by algolia are mocked in e2e test
    return {"offerId": offer.id, "offerName": offer.name, "venueName": newOfferer.venue.name}


def create_pro_user_with_individual_offers() -> dict:
    pro_user = users_factories.ProFactory.create()
    offerer = offerers_factories.OffererFactory.create()
    offerers_factories.UserOffererFactory.create(user=pro_user, offerer=offerer)
    venue = offerers_factories.VenueFactory.create(name="Mon Lieu", managingOfferer=offerer, isPermanent=True)
    offerers_factories.VirtualVenueFactory.create(managingOfferer=offerer)
    offer1 = offers_factories.ThingOfferFactory.create(venue=venue, name="Une super offre")
    offers_factories.StockFactory.create(offer=offer1)
    offer2 = offers_factories.ThingOfferFactory.create(
        venue=venue,
        name="Une offre avec ean",
        ean="1234567891234",
        subcategoryId=subcategories.LIVRE_PAPIER.id,
    )
    offers_factories.StockFactory.create(offer=offer2)
    offer3 = offers_factories.ThingOfferFactory.create(
        venue=venue,
        name="Une flûte traversière",
        subcategoryId=subcategories.ACHAT_INSTRUMENT.id,
    )
    offers_factories.StockFactory.create(offer=offer3)

    offer4 = offers_factories.EventOfferFactory.create(
        venue=venue,
        name="Un concert d'electro inoubliable",
        subcategoryId=subcategories.CONCERT.id,
        extraData={"gtl_id": "04000000"},
    )
    offers_factories.StockFactory.create(offer=offer4)

    offer5 = offers_factories.ThingOfferFactory.create(
        venue=venue,
        name="Une autre offre incroyable",
        subcategoryId=subcategories.LIVRE_PAPIER.id,
    )
    offers_factories.StockFactory.create(offer=offer5)
    offer6 = offers_factories.ThingOfferFactory.create(
        venue=venue,
        name="Encore une offre incroyable",
        subcategoryId=subcategories.LIVRE_PAPIER.id,
    )
    offers_factories.StockFactory.create(offer=offer6)
    offer7 = offers_factories.ThingOfferFactory.create(
        venue=venue,
        name="Une offre épuisée",
        subcategoryId=subcategories.LIVRE_PAPIER.id,
    )
    return {
        "user": get_pro_user_helper(pro_user),
        "venue": {"name": venue.name},
        "offer1": {"name": offer1.name},
        "offer2": {"name": offer2.name},
        "offer3": {"name": offer3.name},
        "offer4": {"name": offer4.name},
        "offer5": {"name": offer5.name},
        "offer6": {"name": offer6.name},
        "offer7": {"name": offer7.name},
    }


def create_pro_user_with_collective_offers() -> dict:
    pro_user = users_factories.ProFactory.create()
    offerer = offerers_factories.OffererFactory.create()
    offerers_factories.UserOffererFactory.create(user=pro_user, offerer=offerer)
    venue1 = offerers_factories.CollectiveVenueFactory.create(name="Mon Lieu 1", managingOfferer=offerer)
    venue2 = offerers_factories.CollectiveVenueFactory.create(name="Mon Lieu 2", managingOfferer=offerer)
    offerers_factories.VirtualVenueFactory.create(managingOfferer=offerer)

    offerPublishedTemplate = educational_factories.CollectiveOfferTemplateFactory.create(
        name="Mon offre collective publiée vitrine",
        venue=venue1,
        formats=[EacFormat.CONCERT],
    )

    offerPublished = educational_factories.CollectiveStockFactory.create(
        collectiveOffer__name="Mon offre collective publiée réservable",
        collectiveOffer__venue=venue1,
        collectiveOffer__formats=[EacFormat.CONCERT],
        startDatetime=datetime.datetime.utcnow() + datetime.timedelta(weeks=2),
        endDatetime=datetime.datetime.utcnow() + datetime.timedelta(weeks=2),
    )

    offerDraft = educational_factories.DraftCollectiveOfferFactory.create(
        name="Mon offre collective en brouillon réservable",
        venue=venue1,
        formats=[EacFormat.REPRESENTATION],
    )

    offerInInstruction = educational_factories.PendingCollectiveOfferFactory.create(
        name="Mon offre collective en instruction réservable",
        venue=venue2,
        formats=[EacFormat.REPRESENTATION],
    )

    offerNotConform = educational_factories.RejectedCollectiveOfferFactory.create(
        name="Mon offre collective non conforme réservable",
        venue=venue2,
        formats=[EacFormat.REPRESENTATION],
    )

    offerArchived = educational_factories.ArchivedCollectiveOfferFactory.create(
        name="Mon offre collective archivée réservable",
        venue=venue2,
        formats=[EacFormat.PROJECTION_AUDIOVISUELLE],
    )

    educational_factories.EducationalDomainFactory.create(
        name="Danse",
    )
    educational_factories.EducationalDomainFactory.create(
        name="Architecture",
    )

    educational_factories.EducationalCurrentYearFactory.create()
    educational_factories.EducationalYearFactory.create()
    educational_factories.EducationalInstitutionFactory.create(name="COLLEGE 123")

    return {
        "user": get_pro_user_helper(pro_user),
        "offerPublishedTemplate": {
            "name": offerPublishedTemplate.name,
            "venueName": offerPublishedTemplate.venue.name,
        },
        "offerPublished": {
            "name": offerPublished.collectiveOffer.name,
            "venueName": offerPublished.collectiveOffer.venue.name,
        },
        "offerDraft": {
            "name": offerDraft.name,
            "venueName": offerDraft.venue.name,
        },
        "offerInInstruction": {
            "name": offerInInstruction.name,
            "venueName": offerInInstruction.venue.name,
        },
        "offerNotConform": {
            "name": offerNotConform.name,
            "venueName": offerNotConform.venue.name,
        },
        "offerArchived": {"name": offerArchived.name, "venueName": offerArchived.venue.name},
    }


def create_pro_user_with_active_collective_offer() -> dict:
    current_year = educational_factories.EducationalCurrentYearFactory.create()

    educational_institution = educational_factories.EducationalInstitutionFactory.create(
        # should match id of user generated in create_adage_jwt_fake_token
        institutionId=UAI_FOR_FAKE_TOKEN,
    )
    educational_factories.EducationalDepositFactory.create(
        educationalInstitution=educational_institution, educationalYear=current_year
    )

    pro_user = users_factories.ProFactory.create()
    offerer = offerers_factories.OffererFactory.create()

    offerers_factories.UserOffererFactory.create(user=pro_user, offerer=offerer)
    venue = offerers_factories.CollectiveVenueFactory.create(name="Mon Lieu", managingOfferer=offerer, isPermanent=True)
    offer = educational_factories.ActiveCollectiveOfferFactory.create(
        name="Mon offre collective",
        institution=educational_institution,
        venue=venue,
        formats=[EacFormat.PROJECTION_AUDIOVISUELLE],
    )

    # Create a provider for the offerer
    provider = providers_factories.PublicApiProviderFactory.create()
    providers_factories.VenueProviderFactory.create(
        venue=venue,
        provider=provider,
    )
    providers_factories.OffererProviderFactory.create(
        offerer=offerer,
        provider=provider,
    )

    key, clear_token = offerers_api.generate_provider_api_key(provider)
    db.session.add(key)
    db.session.commit()

    return {
        "user": get_pro_user_helper(pro_user),
        "offer": {"id": offer.id, "name": offer.name, "venueName": offer.venue.name},
        "stock": {"startDatetime": datetime.datetime.utcnow() + datetime.timedelta(days=10)},
        "providerApiKey": str(clear_token),
    }


def create_pro_user_with_collective_bookings() -> dict:
    pro_user = users_factories.ProFactory.create()
    offerer = offerers_factories.OffererFactory.create()
    offerers_factories.UserOffererFactory.create(user=pro_user, offerer=offerer)
    venue = offerers_factories.VenueFactory.create(name="Mon Lieu", managingOfferer=offerer, isPermanent=True)
    offerers_factories.VirtualVenueFactory.create(managingOfferer=offerer)

    collectiveStock = educational_factories.CollectiveStockFactory.create(
        collectiveOffer__venue=venue,
        collectiveOffer__name="Mon offre",
        startDatetime=datetime.datetime.utcnow() + datetime.timedelta(days=10),
    )
    collectiveStock_B = educational_factories.CollectiveStockFactory.create(
        collectiveOffer__venue=venue, collectiveOffer__name="Mon autre offre"
    )
    educational_factories.CollectiveBookingFactory.create(collectiveStock=collectiveStock)
    educational_factories.CollectiveBookingFactory.create(
        collectiveStock__collectiveOffer__name="Encore une autre offre",
        collectiveStock__startDatetime=datetime.datetime.utcnow() + datetime.timedelta(days=10),
        collectiveStock__collectiveOffer__venue=venue,
        educationalInstitution__name="Autre collège",
    )
    educational_factories.CollectiveBookingFactory.create(
        collectiveStock=collectiveStock_B, educationalInstitution__name="Autre établissement"
    )
    educational_factories.CollectiveBookingFactory.create(
        collectiveStock=collectiveStock_B, educationalInstitution__name="Victor Hugo"
    )
    return {"user": get_pro_user_helper(pro_user)}
