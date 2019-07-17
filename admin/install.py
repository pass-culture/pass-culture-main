from admin.custom_views import OffererAdminView, UserAdminView, FeatureAdminView, VenueAdminView, BeneficiaryImportView
from models import Offerer, User, Feature, Venue
from models.beneficiary_import import BeneficiaryImport


def install_admin_views(admin, session):
    admin.add_view(OffererAdminView(Offerer, session, name='Structures', category='Pro'))
    admin.add_view(UserAdminView(User, session, name='Utilisateurs', category=None))
    admin.add_view(VenueAdminView(Venue, session, name='Lieux', category='Pro'))
    admin.add_view(FeatureAdminView(Feature, session, name='Fonctionnalités', category=None))
    admin.add_view(BeneficiaryImportView(BeneficiaryImport, session, name='Import des bénéficiaires DMS', category=None))
