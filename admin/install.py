from admin.custom_views import OffererAdminView, UserAdminView
from models import Offerer, User


def install_admin_views(admin, session):
    admin.add_view(OffererAdminView(Offerer, session, name='Structures', category='Pro'))
    admin.add_view(UserAdminView(User, session, name='Utilisateurs', category=None))
