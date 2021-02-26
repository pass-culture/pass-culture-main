from flask_admin.form import rules
from sqlalchemy.orm import query
from sqlalchemy.sql.expression import distinct
from sqlalchemy.sql.functions import func
from wtforms import Form
from wtforms import validators
from wtforms.fields.core import Field
from wtforms.fields.core import StringField
from wtforms.validators import ValidationError

from pcapi.admin.base_configuration import BaseAdminView
from pcapi.core.users.models import User
from pcapi.models import UserOfferer
from pcapi.models.offerer import Offerer
from pcapi.validation.models.has_address_mixin import POSTAL_CODE_REGEX

from ...core.offerers.api import create_digital_venue
from ...core.users.api import fulfill_account_password
from .mixins.suspension_mixin import SuspensionMixin


def unique_siren(form: Form, field: Field) -> None:
    if Offerer.query.filter_by(siren=field.data).first():
        raise ValidationError("Une structure avec le même Siren existe déjà.")


def create_offerer(form: Form) -> Offerer:
    offerer = Offerer()
    offerer.siren = form.offererSiren.data
    offerer.name = form.offererName.data
    offerer.postalCode = form.offererPostalCode.data
    offerer.city = form.offererCity.data

    return offerer


def create_user_offerer(user: User, offerer: Offerer) -> UserOfferer:
    user_offerer = UserOfferer()
    user_offerer.user = user
    user_offerer.offerer = offerer

    return user_offerer


class ProUserView(SuspensionMixin, BaseAdminView):
    can_edit = True
    can_create = True
    column_list = [
        "id",
        "isBeneficiary",
        "email",
        "firstName",
        "lastName",
        "publicName",
        "dateOfBirth",
        "departementCode",
        "phoneNumber",
        "postalCode",
        "resetPasswordToken",
        "validationToken",
        "actions",
    ]
    column_labels = dict(
        email="Email",
        isBeneficiary="Est bénéficiaire",
        firstName="Prénom",
        lastName="Nom",
        publicName="Nom d'utilisateur",
        dateOfBirth="Date de naissance",
        departementCode="Département",
        phoneNumber="Numéro de téléphone",
        postalCode="Code postal",
        resetPasswordToken="Jeton d'activation et réinitialisation de mot de passe",
        validationToken="Jeton de validation d'adresse email",
    )
    column_searchable_list = ["id", "publicName", "email", "firstName", "lastName"]
    column_filters = ["postalCode", "isBeneficiary"]
    form_columns = [
        "email",
        "firstName",
        "lastName",
        "dateOfBirth",
        "departementCode",
        "postalCode",
    ]

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
    )

    # This override is necessary to prevent SIREN and offererName to be in edit form as well
    def get_create_form(self) -> Form:
        form = super().get_form()
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
        form.phoneNumber = StringField("Numéro de tél.", [validators.DataRequired()])
        return form

    def on_model_change(self, form: Form, model: User, is_created: bool) -> None:
        model.publicName = f"{model.firstName} {model.lastName}"

        if is_created:
            model.isBeneficiary = False
            fulfill_account_password(model)
            offerer = create_offerer(form)
            create_digital_venue(offerer)
            user_offerer = create_user_offerer(user=model, offerer=offerer)
            model.userOfferers = [user_offerer]

        super().on_model_change(form, model, is_created)

    def get_query(self) -> query:
        return User.query.join(UserOfferer).distinct(User.id).from_self()

    def get_count_query(self) -> query:
        return self.session.query(func.count(distinct(User.id))).select_from(User).join(UserOfferer)
