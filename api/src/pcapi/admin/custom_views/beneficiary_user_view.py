from flask_admin.contrib.sqla import tools
from flask_admin.contrib.sqla.filters import BaseSQLAFilter
from flask_sqlalchemy import BaseQuery
from markupsafe import Markup
from sqlalchemy import and_
from sqlalchemy.orm import aliased
from sqlalchemy.orm import joinedload
from sqlalchemy.sql.functions import func
from wtforms import Form
from wtforms import SelectField
from wtforms.validators import DataRequired

from pcapi import settings
from pcapi.admin.base_configuration import BaseAdminView
from pcapi.admin.custom_views.mixins.resend_validation_email_mixin import ResendValidationEmailMixin
from pcapi.admin.custom_views.mixins.suspension_mixin import SuspensionMixin
from pcapi.core.payments.models import Deposit
from pcapi.core.payments.models import DepositType
import pcapi.core.users.api as users_api
from pcapi.core.users.external import update_external_user
from pcapi.core.users.models import EligibilityType
from pcapi.core.users.models import User
from pcapi.core.users.utils import sanitize_email


def filter_email(value: str | None) -> str | None:
    if not value:
        return value
    return sanitize_email(value)


class FilterByDepositTypeEqual(BaseSQLAFilter):
    def apply(self, query, value, alias=None):  # type: ignore [no-untyped-def]
        aliased_deposit = aliased(Deposit)
        current_deposit_by_user = (
            Deposit.query.outerjoin(
                aliased_deposit,
                and_(Deposit.userId == aliased_deposit.userId, Deposit.expirationDate < aliased_deposit.expirationDate),
            )
            .filter(aliased_deposit.id.is_(None))
            .subquery()
        )
        return query.join(current_deposit_by_user).filter(current_deposit_by_user.c.type == value)

    def operation(self) -> str:
        return "equals"

    def get_options(self, view):  # type: ignore [no-untyped-def]
        return [(deposit_type.name, deposit_type.name) for deposit_type in DepositType]


class FilterByDepositTypeNotEqual(BaseSQLAFilter):
    def apply(self, query, value, alias=None):  # type: ignore [no-untyped-def]
        aliased_deposit = aliased(Deposit)
        current_deposit_by_user = (
            Deposit.query.outerjoin(
                aliased_deposit,
                and_(Deposit.userId == aliased_deposit.userId, Deposit.expirationDate < aliased_deposit.expirationDate),
            )
            .filter(aliased_deposit.id.is_(None))
            .subquery()
        )
        return query.join(current_deposit_by_user).filter(current_deposit_by_user.c.type != value)

    def operation(self) -> str:
        return "not equal"

    def get_options(self, view):  # type: ignore [no-untyped-def]
        return [(deposit_type.name, deposit_type.name) for deposit_type in DepositType]


def beneficiary_deposit_type_formatter(view, context, model, name) -> Markup:  # type: ignore [no-untyped-def]
    colors = {
        DepositType.GRANT_15_17: "#C7CEEA",
        DepositType.GRANT_18: "#FF9AA2",
    }
    return Markup("""<span class="badge" style="background-color:{color}">{deposit_type_name}</span>""").format(
        color=colors.get(model.deposit_type, "#FFFFFF"),
        deposit_type_name=model.deposit_type.name if model.deposit_type else "No deposit",
    )


def beneficiary_total_amount_initial_formatter(view, context, model, name) -> Markup:  # type: ignore [no-untyped-def]
    amount = users_api.get_domains_credit(model)
    all_initial = amount.all.initial if amount else "0"
    return Markup("<span>{all_initial}&nbsp;&euro;</span>").format(all_initial=all_initial)


def beneficiary_total_amount_remaining_formatter(view, context, model, name) -> Markup:  # type: ignore [no-untyped-def]
    amount = users_api.get_domains_credit(model)
    all_remaining = amount.all.remaining if amount else "0"
    return Markup("<span>{all_remaining}&nbsp;&euro;</span>").format(all_remaining=all_remaining)


def beneficiary_physical_remaining_formatter(view, context, model, name) -> Markup:  # type: ignore [no-untyped-def]
    amount = users_api.get_domains_credit(model)
    physical_remaining = amount.physical.remaining if amount and amount.physical else "Pas de plafond"
    return Markup("<span>{physical_remaining}&nbsp;&euro;</span>").format(physical_remaining=physical_remaining)


def beneficiary_digital_remaining_formatter(view, context, model, name) -> Markup:  # type: ignore [no-untyped-def]
    amount = users_api.get_domains_credit(model)
    digital_remaining = amount.digital.remaining if amount and amount.digital else "Pas de plafond"
    return Markup("<span>{digital_remaining}&nbsp;&euro;</span>").format(digital_remaining=digital_remaining)


class BeneficiaryUserView(ResendValidationEmailMixin, SuspensionMixin, BaseAdminView):
    can_edit = True
    can_view_details = True

    @property
    def can_create(self) -> bool:  # type: ignore [override]
        return self.check_super_admins()

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
        "has_active_deposit",
        "deposit_type",
        "deposit_version",
        "actions",
    ]
    column_details_list = [
        "total_initial",
        "total_remaining",
        "digital_remaining",
        "physical_remaining",
        "comment",
        "validationToken",
        "activity",
        "address",
        "city",
        "civility",
        "culturalSurveyFilledDate",
        "culturalSurveyId",
        "dateCreated",
        "dateOfBirth",
        "departementCode",
        "email",
        "externalIds",
        "extraData",
        "firstName",
        "idPieceNumber",
        "ineHash",
        "isActive",
        "isEmailValidated",
        "lastConnectionDate",
        "lastName",
        "needsToFillCulturalSurvey",
        "notificationSubscriptions",
        "phoneNumber",
        "phoneValidationStatus",
        "postalCode",
        "publicName",
        "recreditAmountToShow",
        "roles",
        "subscriptionState",
        "suspension_history",
    ]

    column_labels = dict(
        comment="Commentaire",
        dateOfBirth="Date de naissance",
        departementCode="Département",
        deposit_type="Type du portefeuille",
        deposit_version="Version du portefeuille",
        digital_remaining="Crédit digital restant",
        email="Email",
        firstName="Prénom",
        has_active_deposit="Dépôt valable ?",
        has_beneficiary_role="Bénéficiaire 18 ans ?",
        has_underage_beneficiary_role="Bénéficiaire 15-17 ?",
        idPieceNumber="N° de pièce d'identité",
        isActive="Est activé",
        isEmailValidated="Email validé ?",
        lastName="Nom",
        needsToFillCulturalSurvey="Doit remplir le questionnaire de pratiques culturelles",
        phoneNumber="Numéro de téléphone",
        physical_remaining="Crédit physique restant",
        postalCode="Code postal",
        publicName="Nom d'utilisateur",
        suspension_history="Historique de suspension",
        total_remaining="Crédit global restant",
        total_initial="Crédit initial",
    )

    column_searchable_list = ["id", "publicName", "email", "firstName", "lastName"]
    column_filters = [
        "postalCode",
        "has_beneficiary_role",
        "has_underage_beneficiary_role",
        "isEmailValidated",
        FilterByDepositTypeEqual(column=None, name="Type du portefeuille"),
        FilterByDepositTypeNotEqual(column=None, name="Type du portefeuille"),
        "isActive",
    ]

    @property
    def column_formatters(self):  # type: ignore [no-untyped-def]
        formatters = super().column_formatters
        formatters["deposit_type"] = beneficiary_deposit_type_formatter
        formatters["total_initial"] = beneficiary_total_amount_initial_formatter
        formatters["total_remaining"] = beneficiary_total_amount_remaining_formatter
        formatters["digital_remaining"] = beneficiary_digital_remaining_formatter
        formatters["physical_remaining"] = beneficiary_physical_remaining_formatter

        return formatters

    @property
    def form_columns(self):  # type: ignore [no-untyped-def]
        fields = (
            "email",
            "dateOfBirth",
            "departementCode",
            "postalCode",
            "phoneNumber",
            "needsToFillCulturalSurvey",
        )
        if self.check_super_admins():
            fields += ("firstName", "lastName", "idPieceNumber", "comment")

        return fields

    form_args = dict(
        firstName=dict(validators=[DataRequired()]),
        lastName=dict(validators=[DataRequired()]),
        dateOfBirth=dict(validators=[DataRequired()]),
        postalCode=dict(validators=[DataRequired()]),
        email=dict(validators=[DataRequired()], filters=[filter_email]),
    )

    def get_create_form(self):  # type: ignore [no-untyped-def]
        form_class = super().scaffold_form()

        if not settings.IS_PROD:
            form_class.depositVersion = SelectField(
                "Version du portefeuille",
                [DataRequired()],
                choices=[
                    (1, "500€ - Deux seuils de dépense (300€ en physique et 200€ en numérique)"),
                    (2, "300€ - Un seuil de dépense (100€ en offres numériques)"),
                ],
            )

        return form_class

    def on_model_change(self, form: Form, model: User, is_created: bool) -> None:
        model.publicName = f"{model.firstName} {model.lastName}"

        if is_created:
            model.add_beneficiary_role()

            deposit_version = int(form.depositVersion.data) if not settings.IS_PROD else None
            users_api.fulfill_beneficiary_data(model, "pass-culture-admin", EligibilityType.AGE18, deposit_version)

        super().on_model_change(form, model, is_created)

    def after_model_change(self, form: Form, model: User, is_created: bool) -> None:
        update_external_user(model)
        super().after_model_change(form, model, is_created)

    def get_one(self, model_id: str) -> BaseQuery:
        return User.query.get(tools.iterdecode(model_id))

    def get_query(self) -> BaseQuery:
        return (
            User.query.filter(User.has_pro_role.is_(False))  # type: ignore [attr-defined]
            .filter(User.is_beneficiary.is_(True))  # type: ignore [attr-defined]
            .options(joinedload(User.deposits))
            .options(joinedload(User.suspension_history))
        )

    def get_count_query(self) -> BaseQuery:
        return (
            self.session.query(func.count("*"))
            .select_from(self.model)
            .filter(User.has_pro_role.is_(False))  # type: ignore [attr-defined]
            .filter(User.has_beneficiary_role.is_(True))  # type: ignore [attr-defined]
        )
