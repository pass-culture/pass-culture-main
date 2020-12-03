from flask_admin.base import Admin
from sqlalchemy.orm.session import Session

from pcapi.admin.custom_views import BeneficiaryImportView
from pcapi.admin.custom_views import BeneficiaryUserAdminView
from pcapi.admin.custom_views import CriteriaAdminView
from pcapi.admin.custom_views import FeatureAdminView
from pcapi.admin.custom_views import OfferAdminView
from pcapi.admin.custom_views import OffererAdminView
from pcapi.admin.custom_views import ProUserAdminView
from pcapi.admin.custom_views import VenueAdminView
from pcapi.models import BeneficiaryImport
from pcapi.models import Criterion
from pcapi.models import Feature
from pcapi.models import Offer
from pcapi.models import Offerer
from pcapi.models import UserSQLEntity
from pcapi.models import VenueSQLEntity


def install_admin_views(admin: Admin, session: Session) -> None:
    admin.add_view(OfferAdminView(Offer, session, name="Offres", category="Pro"))
    admin.add_view(CriteriaAdminView(Criterion, session, name="Tags des offres", category="Pro"))
    admin.add_view(OffererAdminView(Offerer, session, name="Structures", category="Pro"))
    admin.add_view(VenueAdminView(VenueSQLEntity, session, name="Lieux", category="Pro"))
    admin.add_view(
        ProUserAdminView(UserSQLEntity, session, name="Comptes Pros", category="Utilisateurs", endpoint="/pro_users")
    )
    admin.add_view(
        BeneficiaryUserAdminView(
            UserSQLEntity, session, name="Comptes Jeunes", category="Utilisateurs", endpoint="/beneficiary_users"
        )
    )
    admin.add_view(BeneficiaryImportView(BeneficiaryImport, session, name="Imports DMS", category="Utilisateurs"))
    admin.add_view(FeatureAdminView(Feature, session, name="Fonctionnalités", category=None))
