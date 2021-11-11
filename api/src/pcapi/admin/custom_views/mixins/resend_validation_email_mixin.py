from flask import flash
from flask import redirect
from flask import request
from flask import url_for
from flask_admin import expose
from flask_admin.form import SecureForm
from markupsafe import Markup

import pcapi.core.users.api as users_api
from pcapi.core.users.models import User


class ResendValidationEmailForm(SecureForm):
    pass  # empty form, only has the CSRF token field


def _format_is_email_validated(view, context, model, name):
    if model.isEmailValidated:
        return True
    url = url_for(".resend_validation_email_view")
    _html = """
     <a href="{url}?user_id={model_id}" title="Réenvoyer l'email de validation">Réenvoyer...</a>
    """.format(
        url=url, model_id=model.id
    )
    return Markup(_html)


class ResendValidationEmailMixin:
    @property
    def column_formatters(self):
        formatters = super().column_formatters
        formatters.update(isEmailValidated=_format_is_email_validated)
        return formatters

    @property
    def user_list_url(self):
        return url_for(".index_view")

    @expose("resend-validation-email", ["GET", "POST"])
    def resend_validation_email_view(self):
        user_id = request.args["user_id"]
        user = User.query.get(user_id)
        if user.has_admin_role or user.has_pro_role:
            flash("Cette action n'est pas supportée pour les utilisateurs admin ou pro", "error")
            return redirect(self.user_list_url)

        if request.method == "POST":
            form = ResendValidationEmailForm(request.form)
            if form.validate():
                flash(f"Un lien de confirmation d'email a été envoyé à l'adresse {user.email}.")
                if not user.isEmailValidated:
                    users_api.request_email_confirmation(user)
                    return redirect(self.user_list_url)
        else:
            form = ResendValidationEmailForm()

        context = {
            "cancel_link_url": self.user_list_url,
            "form": form,
            "user": user,
        }
        return self.render("admin/resend_validation_email.html", **context)
