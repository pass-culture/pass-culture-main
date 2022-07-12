import datetime

from flask.helpers import flash
from flask_admin.form import rules
from flask_login import current_user
from flask_sqlalchemy import BaseQuery
from sqlalchemy.sql.expression import distinct
from sqlalchemy.sql.functions import func
from wtforms import Form
from wtforms import validators
from wtforms.fields import Field
from wtforms.fields import HiddenField
from wtforms.fields import StringField
from wtforms.validators import DataRequired
from wtforms.validators import ValidationError

from pcapi.admin.base_configuration import BaseAdminView
import pcapi.admin.rules as pcapi_rules
from pcapi.admin.validators import PhoneNumberValidator
from pcapi.core.mails.transactional.pro.reset_password_to_pro import send_reset_password_link_to_admin_email
import pcapi.core.offerers.api as offerers_api
import pcapi.core.offerers.models as offerers_models
import pcapi.core.users.api as users_api
from pcapi.core.users.constants import RESET_PASSWORD_TOKEN_LIFE_TIME_EXTENDED
from pcapi.core.users.external import update_external_pro
from pcapi.core.users.models import User
from pcapi.core.users.utils import sanitize_email
from pcapi.utils.mailing import build_pc_pro_create_password_link
from pcapi.validation.models.has_address_mixin import POSTAL_CODE_REGEX

from .mixins.suspension_mixin import SuspensionMixin


def unique_siren(form: Form, field: Field) -> None:
    if offerers_models.Offerer.query.filter_by(siren=field.data).one_or_none():
        raise ValidationError("Une structure avec le même Siren existe déjà.")


def filter_email(value: str | None) -> str | None:
    if not value:
        return value
    return sanitize_email(value)


def create_offerer(form: Form) -> offerers_models.Offerer:
    offerer = offerers_models.Offerer()
    offerer.siren = form.offererSiren.data
    offerer.name = form.offererName.data
    offerer.postalCode = form.offererPostalCode.data
    offerer.city = form.offererCity.data

    return offerer


def create_user_offerer(user: User, offerer: offerers_models.Offerer) -> offerers_models.UserOfferer:
    user_offerer = offerers_models.UserOfferer()
    user_offerer.user = user
    user_offerer.offerer = offerer

    return user_offerer


class ProUserView(SuspensionMixin, BaseAdminView):
    can_edit = True
    can_create = True
    can_view_details = True

    column_list = [
        "id",
        "isActive",
        "email",
        "firstName",
        "lastName",
        "publicName",
        "dateOfBirth",
        "departementCode",
        "phoneNumber",
        "postalCode",
        "isEmailValidated",
        "validationToken",
        "actions",
    ]
    column_labels = dict(
        comment="Commentaire",
        email="Email",
        isActive="Est activé",
        firstName="Prénom",
        lastName="Nom",
        publicName="Nom d'utilisateur",
        dateOfBirth="Date de naissance",
        departementCode="Département",
        phoneNumber="Numéro de téléphone",
        postalCode="Code postal",
        isEmailValidated="Email validé ?",
        validationToken="Jeton de validation d'adresse email",
        has_beneficiary_role="Bénéficiaire 18 ans ?",
        has_underage_beneficiary_role="Bénéficiaire 15-17 ?",
        suspension_history="Historique de suspension",
    )
    column_searchable_list = ["id", "publicName", "email", "firstName", "lastName"]
    column_filters = ["postalCode", "has_beneficiary_role", "has_underage_beneficiary_role", "isEmailValidated"]
    column_details_list = ["suspension_history", "comment"]

    form_create_rules = (
        rules.Header("Utilisateur créé :"),
        "email",
        "firstName",
        "lastName",
        "phoneNumber",
        "dateOfBirth",
        "departementCode",
        "postalCode",
        rules.Header("Structure créée :"),
        "offererSiren",
        "offererName",
        "offererPostalCode",
        "offererCity",
        pcapi_rules.HiddenField("comment"),
        pcapi_rules.HiddenField("csrf_token"),
    )

    @property
    def form_columns(self):  # type: ignore [no-untyped-def]
        fields = (
            "email",
            "firstName",
            "lastName",
            "dateOfBirth",
            "departementCode",
            "postalCode",
            "phoneNumber",
        )
        if self.check_super_admins():
            fields += ("comment",)
        return fields

    # This override is necessary to prevent SIREN and offererName to be in edit form as well
    def get_create_form(self) -> Form:
        form = super().get_form()
        form.email = StringField("Email", [DataRequired()], filters=[filter_email])
        form.postalCode = StringField("Code postal", [validators.DataRequired()])
        form.offererSiren = StringField(
            "SIREN",
            [validators.DataRequired(), validators.Length(9, 9, "Un SIREN contient 9 caractères"), unique_siren],
        )
        form.offererName = StringField("Nom de la structure", [validators.DataRequired()])
        form.offererPostalCode = StringField(
            "Code postal de la structure",
            [
                validators.DataRequired(),
                validators.Regexp(POSTAL_CODE_REGEX, message="Le code postal saisi doit être valide"),
            ],
        )
        form.offererCity = StringField("Ville de la structure", [validators.DataRequired()])
        form.firstName = StringField("Prénom", [validators.DataRequired()])
        form.lastName = StringField("Nom", [validators.DataRequired()])
        form.phoneNumber = StringField("Numéro de téléphone", [validators.DataRequired(), PhoneNumberValidator()])
        # We require a SIREN, which means that "comment" must be empty
        # (see model constraints), which is why the field is hidden.
        form.comment = HiddenField()
        return form

    def get_edit_form(self) -> Form:
        form = super().get_form()
        form.email = StringField("Email", [DataRequired()], filters=[filter_email])
        form.phoneNumber = StringField("Numéro de téléphone", [PhoneNumberValidator()])
        return form

    def on_model_change(self, form: Form, model: User, is_created: bool) -> None:
        model.publicName = f"{model.firstName} {model.lastName}"

        if is_created:
            model.remove_beneficiary_role()
            model.add_pro_role()
            users_api.fulfill_account_password(model)
            offerer = create_offerer(form)
            offerers_api.create_digital_venue(offerer)
            user_offerer = create_user_offerer(user=model, offerer=offerer)
            model.userOfferers = [user_offerer]
        super().on_model_change(form, model, is_created)

    def after_model_change(self, form: Form, model: User, is_created: bool) -> None:
        if is_created:
            resetPasswordToken = users_api.create_reset_password_token(
                model,
                expiration=datetime.datetime.utcnow() + RESET_PASSWORD_TOKEN_LIFE_TIME_EXTENDED,
            )
            reset_password_link = build_pc_pro_create_password_link(resetPasswordToken.value)
            flash(f"Lien de création de mot de passe : {reset_password_link}")
            if current_user:
                send_reset_password_link_to_admin_email(model, current_user.email, reset_password_link)
        super().after_model_change(form, model, is_created)

        update_external_pro(model.email)

    def get_query(self) -> BaseQuery:
        return User.query.join(offerers_models.UserOfferer).distinct(User.id).from_self()

    def get_count_query(self) -> BaseQuery:
        return self.session.query(func.count(distinct(User.id))).select_from(User).join(offerers_models.UserOfferer)
