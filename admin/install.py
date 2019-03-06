from admin.custom_views import OffererAdminView
from models import Offerer


def install_admin_views(admin, session):
    admin.add_view(OffererAdminView(Offerer, session, name='Structures', category='Pro'))
