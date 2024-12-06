import datetime

from pcapi.core.bookings import models as bookings_models
import pcapi.core.bookings.factories as bookings_factories
from pcapi.core.categories import subcategories_v2 as subcategories
from pcapi.core.educational import models as educational_models
import pcapi.core.educational.factories as educational_factories
from pcapi.core.finance import factories as finance_factories
import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offers.factories as offers_factories
from pcapi.core.users import factories as users_factories
from pcapi.sandboxes.scripts.utils.helpers import get_pro_user_helper


def create_new_pro_user() -> dict:
    pro_user = users_factories.ProFactory()
    return {"user": get_pro_user_helper(pro_user)}


def create_new_pro_user_and_offerer() -> dict:
    pro_user = users_factories.ProFactory()
    offerer = offerers_factories.OffererFactory()
    offerers_factories.VirtualVenueFactory(managingOfferer=offerer)
    return {"user": get_pro_user_helper(pro_user), "siren": offerer.siren}


def create_new_pro_user_and_offerer_with_venue() -> dict:
    pro_user = users_factories.ProFactory()
    offerer = offerers_factories.OffererFactory()
    venue = offerers_factories.VenueFactory(managingOfferer=offerer, isPermanent=True)
    offerers_factories.VirtualVenueFactory(managingOfferer=offerer)
    return {"user": get_pro_user_helper(pro_user), "siret": venue.siret}


def create_regular_pro_user() -> dict:
    pro_user = users_factories.ProFactory()
    offerer = offerers_factories.OffererFactory()
    offerers_factories.UserOffererFactory(user=pro_user, offerer=offerer)
    offerers_factories.VenueFactory(name="Mon Lieu", managingOfferer=offerer, isPermanent=True)
    offerers_factories.VirtualVenueFactory(managingOfferer=offerer)
    offerers_factories.VenueLabelFactory(label="Musée de France")

    return {"user": get_pro_user_helper(pro_user), "siren": offerer.siren}


def create_pro_user_with_bookings() -> dict:
    pro_user = users_factories.ProFactory()
    offerer = offerers_factories.OffererFactory()
    offerers_factories.UserOffererFactory(user=pro_user, offerer=offerer)
    venue = offerers_factories.VenueFactory(name="Mon Lieu", managingOfferer=offerer, isPermanent=True)
    offerers_factories.VirtualVenueFactory(managingOfferer=offerer)
    stock = offers_factories.StockFactory(offer__venue=venue)
    stock_event = offers_factories.EventStockFactory(offer__venue=venue)

    bookings_factories.BookingFactory(token="2XTM3W", stock=stock, status=bookings_models.BookingStatus.CONFIRMED)
    bookings_factories.BookingFactory(token="TOSOON", stock=stock_event, status=bookings_models.BookingStatus.CONFIRMED)
    bookings_factories.BookingFactory(token="XUSEDX", stock=stock, status=bookings_models.BookingStatus.USED)
    bookings_factories.BookingFactory(token="CANCEL", stock=stock, status=bookings_models.BookingStatus.CANCELLED)
    bookings_factories.BookingFactory(token="REIMBU", stock=stock, status=bookings_models.BookingStatus.REIMBURSED)
    bookings_factories.BookingFactory(token="OTHERX")
    return {"user": get_pro_user_helper(pro_user)}


def create_regular_pro_user_with_virtual_offer() -> dict:
    pro_user = users_factories.ProFactory()
    offerer = offerers_factories.OffererFactory()
    offerers_factories.UserOffererFactory(user=pro_user, offerer=offerer)
    offerers_factories.VenueFactory(name="Mon Lieu", managingOfferer=offerer, isPermanent=True)
    virtual_venue = offerers_factories.VirtualVenueFactory(managingOfferer=offerer)
    offers_factories.OfferFactory(
        name="Mon offre virtuelle", subcategoryId=subcategories.ABO_PLATEFORME_VIDEO.id, venue=virtual_venue
    )
    return {"user": get_pro_user_helper(pro_user)}


def create_pro_user_with_financial_data() -> dict:
    pro_user = users_factories.ProFactory()
    offerer_A = offerers_factories.OffererFactory()
    offerers_factories.UserOffererFactory(user=pro_user, offerer=offerer_A)
    offerers_factories.VenueFactory(name="Mon Lieu", managingOfferer=offerer_A)
    offerers_factories.VirtualVenueFactory(managingOfferer=offerer_A)

    offerer_B = offerers_factories.OffererFactory(name="Structure avec informations bancaires")
    offerers_factories.UserOffererFactory(user=pro_user, offerer=offerer_B)
    venue_B = offerers_factories.VenueFactory(name="Mon Lieu", managingOfferer=offerer_B)
    offerers_factories.VirtualVenueFactory(managingOfferer=offerer_B)
    bank_account_B = finance_factories.BankAccountFactory(offerer=offerer_B)
    offerers_factories.VenuePricingPointLinkFactory(
        venue=venue_B,
        pricingPoint=venue_B,
    )
    finance_factories.InvoiceFactory(bankAccount=bank_account_B)

    return {"user": get_pro_user_helper(pro_user)}


def create_pro_user_with_financial_data_and_3_venues() -> dict:
    pro_user = users_factories.ProFactory()

    offerer_C = offerers_factories.OffererFactory(name="Structure avec informations bancaires et 3 lieux")
    offerers_factories.UserOffererFactory(user=pro_user, offerer=offerer_C)
    venue_C = offerers_factories.VenueFactory(name="Mon lieu 1", managingOfferer=offerer_C)
    venue_D = offerers_factories.VenueFactory(name="Mon lieu 2", managingOfferer=offerer_C)
    venue_E = offerers_factories.VenueFactory(name="Mon lieu 3", managingOfferer=offerer_C)
    offerers_factories.VirtualVenueFactory(managingOfferer=offerer_C)
    bank_account_C = finance_factories.BankAccountFactory(offerer=offerer_C)
    offerers_factories.VenuePricingPointLinkFactory(
        venue=venue_C,
        pricingPoint=venue_C,
    )
    offerers_factories.VenuePricingPointLinkFactory(
        venue=venue_D,
        pricingPoint=venue_D,
    )
    offerers_factories.VenuePricingPointLinkFactory(
        venue=venue_E,
        pricingPoint=venue_E,
    )
    finance_factories.InvoiceFactory(bankAccount=bank_account_C)
    finance_factories.InvoiceFactory(bankAccount=bank_account_C)
    finance_factories.InvoiceFactory(bankAccount=bank_account_C)

    return {"user": get_pro_user_helper(pro_user)}


def create_adage_environnement() -> dict:
    current_year = educational_factories.EducationalCurrentYearFactory()
    next_year = educational_factories.EducationalYearFactory()

    offer = educational_factories.CollectiveOfferTemplateFactory(name="Mon offre collective")

    educational_institution = educational_factories.EducationalInstitutionFactory(
        # should match id of user generated in create_adage_jwt_fake_token
        institutionId="0910620E",
    )
    educational_factories.PlaylistFactory(
        distanceInKm=50,
        collective_offer_template=offer,
        type=educational_models.PlaylistType.NEW_OFFER,
        institution=educational_institution,
    )
    educational_factories.PlaylistFactory(
        distanceInKm=50,
        collective_offer_template=offer,
        type=educational_models.PlaylistType.NEW_OFFERER,
        institution=educational_institution,
        venue__name="Mon lieu collectif",
    )
    educational_factories.EducationalDepositFactory(
        educationalInstitution=educational_institution,
        educationalYear=current_year,
        amount=40000,
    )
    educational_factories.EducationalDepositFactory(
        educationalInstitution=educational_institution,
        educationalYear=next_year,
        amount=50000,
        isFinal=False,
    )

    # offer result by algolia are mocked in e2e test
    return {"offerId": offer.id}


def create_pro_user_with_individual_offers() -> dict:
    pro_user = users_factories.ProFactory()
    offerer = offerers_factories.OffererFactory()
    offerers_factories.UserOffererFactory(user=pro_user, offerer=offerer)
    venue = offerers_factories.VenueFactory(name="Mon Lieu", managingOfferer=offerer, isPermanent=True)
    offerers_factories.VirtualVenueFactory(managingOfferer=offerer)
    offer1 = offers_factories.ThingOfferFactory(venue=venue, name="Une super offre")
    offers_factories.StockFactory(offer=offer1)
    offer2 = offers_factories.ThingOfferFactory(
        venue=venue,
        name="Une offre avec ean",
        extraData=dict({"ean": "1234567891234"}),
        subcategoryId=subcategories.LIVRE_PAPIER.id,
    )
    offers_factories.StockFactory(offer=offer2)
    offer3 = offers_factories.ThingOfferFactory(
        venue=venue,
        name="Une flûte traversière",
        subcategoryId=subcategories.ACHAT_INSTRUMENT.id,
    )
    offers_factories.StockFactory(offer=offer3)

    offer4 = offers_factories.EventOfferFactory(
        venue=venue,
        name="Un concert d'electro inoubliable",
        subcategoryId=subcategories.CONCERT.id,
        extraData={"gtl_id": "04000000"},
    )
    offers_factories.StockFactory(offer=offer4)

    offer5 = offers_factories.ThingOfferFactory(
        venue=venue,
        name="Une autre offre incroyable",
        subcategoryId=subcategories.LIVRE_PAPIER.id,
    )
    offers_factories.StockFactory(offer=offer5)
    offer6 = offers_factories.ThingOfferFactory(
        venue=venue,
        name="Encore une offre incroyable",
        subcategoryId=subcategories.LIVRE_PAPIER.id,
    )
    offers_factories.StockFactory(offer=offer6)
    offers_factories.ThingOfferFactory(
        venue=venue,
        name="Une offre épuisée",
        subcategoryId=subcategories.LIVRE_PAPIER.id,
    )
    return {"user": get_pro_user_helper(pro_user)}


def create_pro_user_with_collective_offers() -> dict:
    pro_user = users_factories.ProFactory()
    offerer = offerers_factories.OffererFactory()
    offerers_factories.UserOffererFactory(user=pro_user, offerer=offerer)
    venue1 = offerers_factories.CollectiveVenueFactory(name="Mon Lieu 1", managingOfferer=offerer)
    venue2 = offerers_factories.CollectiveVenueFactory(name="Mon Lieu 2", managingOfferer=offerer)
    offerers_factories.VirtualVenueFactory(managingOfferer=offerer)

    educational_factories.CollectiveOfferTemplateFactory(
        name="Mon offre collective publiée vitrine",
        venue=venue1,
        subcategoryId=subcategories.CONCERT.id,
        formats=[subcategories.EacFormat.CONCERT],
    )

    educational_factories.CollectiveStockFactory(
        collectiveOffer__name="Mon offre collective publiée réservable",
        collectiveOffer__venue=venue1,
        collectiveOffer__subcategoryId=subcategories.CONCERT.id,
        collectiveOffer__formats=[subcategories.EacFormat.CONCERT],
        beginningDatetime=datetime.datetime.utcnow() + datetime.timedelta(weeks=2),
        endDatetime=datetime.datetime.utcnow() + datetime.timedelta(weeks=2),
    )

    educational_factories.DraftCollectiveOfferFactory(
        name="Mon offre collective en brouillon réservable",
        venue=venue1,
        subcategoryId=subcategories.CONCERT.id,
        formats=[subcategories.EacFormat.REPRESENTATION],
    )

    educational_factories.PendingCollectiveOfferFactory(
        name="Mon offre collective en instruction réservable",
        venue=venue2,
        subcategoryId=subcategories.SPECTACLE_REPRESENTATION.id,
        formats=[subcategories.EacFormat.REPRESENTATION],
    )

    educational_factories.RejectedCollectiveOfferFactory(
        name="Mon offre collective non conforme réservable",
        venue=venue2,
        subcategoryId=subcategories.SPECTACLE_REPRESENTATION.id,
        formats=[subcategories.EacFormat.REPRESENTATION],
    )

    educational_factories.ArchivedCollectiveOfferFactory(
        name="Mon offre collective archivée réservable",
        venue=venue2,
        subcategoryId=subcategories.SEANCE_CINE.id,
        formats=[subcategories.EacFormat.PROJECTION_AUDIOVISUELLE],
    )

    educational_factories.EducationalDomainFactory(
        name="Danse",
    )
    educational_factories.EducationalDomainFactory(
        name="Architecture",
    )

    educational_factories.EducationalCurrentYearFactory()
    educational_factories.EducationalYearFactory()
    educational_factories.EducationalInstitutionFactory(name="COLLEGE 123")

    return {"user": get_pro_user_helper(pro_user)}


def create_pro_user_with_collective_bookings() -> dict:
    pro_user = users_factories.ProFactory()
    offerer = offerers_factories.OffererFactory()
    offerers_factories.UserOffererFactory(user=pro_user, offerer=offerer)
    venue = offerers_factories.VenueFactory(name="Mon Lieu", managingOfferer=offerer, isPermanent=True)
    offerers_factories.VirtualVenueFactory(managingOfferer=offerer)

    collectiveStock = educational_factories.CollectiveStockFactory(
        collectiveOffer__venue=venue,
        collectiveOffer__name="Mon offre",
        beginningDatetime=datetime.datetime.utcnow() + datetime.timedelta(days=10),
    )
    collectiveStock_B = educational_factories.CollectiveStockFactory(
        collectiveOffer__venue=venue, collectiveOffer__name="Mon autre offre"
    )
    educational_factories.CollectiveBookingFactory(collectiveStock=collectiveStock)
    educational_factories.CollectiveBookingFactory(
        collectiveStock__collectiveOffer__name="Encore une autre offre",
        collectiveStock__beginningDatetime=datetime.datetime.utcnow() + datetime.timedelta(days=10),
        collectiveStock__collectiveOffer__venue=venue,
        educationalInstitution__name="Autre collège",
    )
    educational_factories.CollectiveBookingFactory(
        collectiveStock=collectiveStock_B, educationalInstitution__name="Autre établissement"
    )
    educational_factories.CollectiveBookingFactory(
        collectiveStock=collectiveStock_B, educationalInstitution__name="Victor Hugo"
    )
    return {"user": get_pro_user_helper(pro_user)}
