from pcapi.core.educational import models as educational_models
import pcapi.core.educational.factories as educational_factories
import pcapi.core.offerers.factories as offerers_factories
from pcapi.core.users import factories as users_factories
from pcapi.sandboxes.scripts.utils.helpers import get_pro_user_helper


def create_new_pro_user() -> dict:
    pro_user = users_factories.ProFactory()
    return {"user": get_pro_user_helper(pro_user)}


def create_new_pro_user_and_offerer() -> dict:
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
