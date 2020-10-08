from pcapi.admin.custom_views import OffererAdminView, UserAdminView, FeatureAdminView, VenueAdminView, BeneficiaryImportView, \
    OfferAdminView, CriteriaAdminView
from pcapi.models import Offerer, UserSQLEntity, Feature, VenueSQLEntity, BeneficiaryImport, OfferSQLEntity, Criterion


def install_admin_views(admin, session):
    admin.add_view(OfferAdminView(OfferSQLEntity, session, name='Offres', category='Pro'))
    admin.add_view(CriteriaAdminView(Criterion, session, name='Tags des offres', category='Pro'))
    admin.add_view(OffererAdminView(Offerer, session, name='Structures', category='Pro'))
    admin.add_view(VenueAdminView(VenueSQLEntity, session, name='Lieux', category='Pro'))
    admin.add_view(UserAdminView(UserSQLEntity, session, name='Comptes', category='Utilisateurs'))
    admin.add_view(BeneficiaryImportView(BeneficiaryImport, session, name='Imports DMS', category='Utilisateurs'))
    admin.add_view(FeatureAdminView(Feature, session, name='Fonctionnalités', category=None))
