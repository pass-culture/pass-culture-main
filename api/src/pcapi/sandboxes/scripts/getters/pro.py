from pcapi.core.categories import subcategories_v2 as subcategories
from pcapi.core.educational import models as educational_models
import pcapi.core.educational.factories as educational_factories
import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offers.factories as offers_factories
from pcapi.core.users import factories as users_factories
from pcapi.repository.clean_database import clean_all_database
from pcapi.sandboxes.scripts.utils.helpers import get_pro_user_helper


def create_new_pro_user() -> dict:
    pro_user = users_factories.ProFactory()
    return {"user": get_pro_user_helper(pro_user)}


def create_new_pro_user_and_offerer() -> dict:
    pro_user = users_factories.ProFactory()
    offerer = offerers_factories.E2EOffererFactory()
    venue = offerers_factories.VenueFactory(managingOfferer=offerer, isPermanent=True)
    offerers_factories.VirtualVenueFactory(managingOfferer=offerer)
    return {"user": get_pro_user_helper(pro_user), "siret": venue.siret}


def create_regular_pro_user() -> dict:
    pro_user = users_factories.ProFactory()
    offerer = offerers_factories.E2EOffererFactory()
    offerers_factories.UserOffererFactory(user=pro_user, offerer=offerer)
    offerers_factories.VenueFactory(name="Mon Lieu", managingOfferer=offerer, isPermanent=True)
    offerers_factories.VirtualVenueFactory(managingOfferer=offerer)
    offerers_factories.VenueLabelFactory(label="Musée de France")

    return {"user": get_pro_user_helper(pro_user), "siren": offerer.siren}


def create_regular_pro_user_with_virtual_offer() -> dict:
    pro_user = users_factories.ProFactory()
    offerer = offerers_factories.E2EOffererFactory()
    offerers_factories.UserOffererFactory(user=pro_user, offerer=offerer)
    offerers_factories.VenueFactory(name="Mon Lieu", managingOfferer=offerer, isPermanent=True)
    virtual_venue = offerers_factories.VirtualVenueFactory(managingOfferer=offerer)
    offers_factories.OfferFactory(
        name="Mon offre virtuelle", subcategoryId=subcategories.ABO_PLATEFORME_VIDEO.id, venue=virtual_venue
    )
    return {"user": get_pro_user_helper(pro_user)}


def create_adage_environnement() -> dict:
    clean_all_database(reset_ids=True)
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
    offerer = offerers_factories.E2EOffererFactory()
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
    offerer = offerers_factories.E2EOffererFactory()
    offerers_factories.UserOffererFactory(user=pro_user, offerer=offerer)
    venue = offerers_factories.VenueFactory(name="Mon Lieu", managingOfferer=offerer, isPermanent=True)
    offerers_factories.VirtualVenueFactory(managingOfferer=offerer)

    educational_factories.CollectiveOfferTemplateFactory(
        name="Mon offre collective",
        venue=venue,
        subcategoryId=subcategories.SEANCE_CINE.id,
        formats=[subcategories.EacFormat.PROJECTION_AUDIOVISUELLE],
    )
    return {"user": get_pro_user_helper(pro_user)}
