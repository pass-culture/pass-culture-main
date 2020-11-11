from flask import url_for
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user
from werkzeug.utils import redirect

from pcapi.utils.logger import logger


class BaseAdminView(ModelView):
    page_size = 25
    can_set_page_size = True
    can_create = False
    can_edit = False
    can_delete = False

    def is_accessible(self):
        authorized = current_user.is_authenticated and current_user.isAdmin

        if authorized:
            logger.info("[ADMIN] Accès autorisé à l'interface d'administation pour %s" % current_user)
        else:
            logger.warning("[ADMIN] Tentative d'accès non autorisé à l'interface d'administation par %s" % current_user)

        return authorized

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for("admin.index"))

    def after_model_change(self, form, model, is_created):
        action = "Création" if is_created else "Modification"
        model_name = str(model)
        logger.info("[ADMIN] %s du modèle %s par l'utilisateur %s" % (action, model_name, current_user))
