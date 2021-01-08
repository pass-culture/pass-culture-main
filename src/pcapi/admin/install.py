from enum import Enum

from flask_admin.base import Admin
from sqlalchemy.orm.session import Session

from pcapi.admin.custom_views.allocine_pivot_view import AllocinePivotView
from pcapi.admin.custom_views.beneficiary_import_view import BeneficiaryImportView
from pcapi.admin.custom_views.beneficiary_user_view import BeneficiaryUserView
from pcapi.admin.custom_views.criteria_view import CriteriaView
from pcapi.admin.custom_views.feature_view import FeatureView
from pcapi.admin.custom_views.offer_view import OfferView
from pcapi.admin.custom_views.offerer_view import OffererView
from pcapi.admin.custom_views.partner_user_view import PartnerUserView
from pcapi.admin.custom_views.pro_user_view import ProUserView
from pcapi.admin.custom_views.user_offerer_view import UserOffererView
from pcapi.admin.custom_views.venue_view import VenueView
from pcapi.core.users.models import User
from pcapi.models import AllocinePivot
from pcapi.models import BeneficiaryImport
from pcapi.models import Criterion
from pcapi.models import Feature
from pcapi.models import Offer
from pcapi.models import Offerer
from pcapi.models import UserOfferer
from pcapi.models import VenueSQLEntity


class Category(Enum):
    def __str__(self) -> str:
        return str(self.value)

    OFFRES_STRUCTURES_LIEUX = "Offre, Lieux & Structure"
    USERS = "Utilisateurs"


def install_admin_views(admin: Admin, session: Session) -> None:
    admin.add_view(OfferView(Offer, session, name="Offres", category=Category.OFFRES_STRUCTURES_LIEUX))
    admin.add_view(CriteriaView(Criterion, session, name="Tags des offres", category=Category.OFFRES_STRUCTURES_LIEUX))
    admin.add_view(OffererView(Offerer, session, name="Structures", category=Category.OFFRES_STRUCTURES_LIEUX))
    admin.add_view(VenueView(VenueSQLEntity, session, name="Lieux", category=Category.OFFRES_STRUCTURES_LIEUX))
    admin.add_view(
        UserOffererView(
            UserOfferer, session, name="Lien Utilisateurs/Structures", category=Category.OFFRES_STRUCTURES_LIEUX
        )
    )
    admin.add_view(
        ProUserView(
            User,
            session,
            name="Comptes Pros",
            category=Category.USERS,
            endpoint="/pro_users",
        )
    )
    admin.add_view(
        BeneficiaryUserView(
            User,
            session,
            name="Comptes Jeunes/Grand Public",
            category=Category.USERS,
            endpoint="/beneficiary_users",
        )
    )
    admin.add_view(
        PartnerUserView(User, session, name="Comptes Partenaires", category=Category.USERS, endpoint="/partner_users")
    )
    admin.add_view(FeatureView(Feature, session, name="Fonctionnalités", category=None))
    admin.add_view(BeneficiaryImportView(BeneficiaryImport, session, name="Imports DMS", category=Category.USERS))
    admin.add_view(
        AllocinePivotView(AllocinePivot, session, name="Pivot Allocine", category=Category.OFFRES_STRUCTURES_LIEUX)
    )
