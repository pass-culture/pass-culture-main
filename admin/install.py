from admin.custom_views import OffererAdminView, UserAdminView, VenueAdminView
from models import Offerer, User, Venue


def install_admin_views(admin, session):
    admin.add_view(OffererAdminView(Offerer, session, name='Structures', category='Pro'))
    admin.add_view(UserAdminView(User, session, name='Utilisateurs', category=None))
    admin.add_view(VenueAdminView(Venue, session, name='Lieux', category='Pro'))
