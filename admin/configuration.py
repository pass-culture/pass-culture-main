from flask import url_for
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user
from werkzeug.utils import redirect

from models import Offerer

HAS_THUMB_COLUMNS = ['thumbCount', 'firstThumbDominantColor']
PROVIDABLE_COLUMNS = ['idAtProviders', 'dateModifiedAtLastProvider']


class BaseAdminView(ModelView):
    page_size = 25
    can_create = False
    can_edit = False
    can_delete = False
    can_export = False

    def is_accessible(self):
        return current_user.is_authenticated and current_user.isAdmin

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('admin.index'))


class OffererAdminView(BaseAdminView):
    can_edit = True
    can_view_details = True
    column_list = ['name', 'siren', 'address', 'postalCode', 'city']
    column_searchable_list = ['name', 'siren']
    column_filters = ['postalCode', 'city']


def install_admin_views(admin, session):
    admin.add_view(OffererAdminView(Offerer, session))
