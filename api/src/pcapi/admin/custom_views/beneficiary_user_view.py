import datetime
import logging
import typing

from flask_admin.contrib.sqla import tools
from flask_admin.contrib.sqla.filters import BaseSQLAFilter
from flask_sqlalchemy import BaseQuery
from markupsafe import Markup
from sqlalchemy import and_
from sqlalchemy.orm import Query
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
from pcapi.core.external.attributes.api import update_external_user
from pcapi.core.finance.api import compute_underage_deposit_expiration_datetime
import pcapi.core.finance.models as finance_models
import pcapi.core.users.api as users_api
from pcapi.core.users.models import EligibilityType
from pcapi.core.users.models import User
from pcapi.repository import repository
from pcapi.utils.email import sanitize_email


logger = logging.getLogger(__name__)


def filter_email(value: str | None) -> str | None:
    if not value:
        return value
    return sanitize_email(value)


class FilterByDepositTypeEqual(BaseSQLAFilter):
    def apply(self, query: Query, value: typing.Any, alias: str | None = None) -> Query:
        aliased_deposit = aliased(finance_models.Deposit)
        current_deposit_by_user = (
            finance_models.Deposit.query.outerjoin(
                aliased_deposit,
                and_(
                    finance_models.Deposit.userId == aliased_deposit.userId,
                    finance_models.Deposit.expirationDate < aliased_deposit.expirationDate,
                ),
            )
            .filter(aliased_deposit.id.is_(None))
            .subquery()
        )
        return query.join(current_deposit_by_user).filter(current_deposit_by_user.c.type == value)

    def operation(self) -> str:
        return "equals"

    def get_options(self, view: BaseAdminView) -> list[tuple[str, str]]:
        return [(deposit_type.name, deposit_type.name) for deposit_type in finance_models.DepositType]


class FilterByDepositTypeNotEqual(BaseSQLAFilter):
    def apply(self, query: Query, value: typing.Any, alias: str | None = None) -> Query:
        aliased_deposit = aliased(finance_models.Deposit)
        current_deposit_by_user = (
            finance_models.Deposit.query.outerjoin(
                aliased_deposit,
                and_(
                    finance_models.Deposit.userId == aliased_deposit.userId,
                    finance_models.Deposit.expirationDate < aliased_deposit.expirationDate,
                ),
            )
            .filter(aliased_deposit.id.is_(None))
            .subquery()
        )
        return query.join(current_deposit_by_user).filter(current_deposit_by_user.c.type != value)

    def operation(self) -> str:
        return "not equal"

    def get_options(self, view: BaseAdminView) -> list[tuple[str, str]]:
        return [(deposit_type.name, deposit_type.name) for deposit_type in finance_models.DepositType]


def beneficiary_deposit_type_formatter(view, context, model, name) -> Markup:  # type: ignore [no-untyped-def]
    colors = {
        finance_models.DepositType.GRANT_15_17: "#C7CEEA",
        finance_models.DepositType.GRANT_18: "#FF9AA2",
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


def _has_underage_deposit(user: User) -> bool:
    return user.deposit is not None and user.deposit.type == finance_models.DepositType.GRANT_15_17


def _update_underage_beneficiary_deposit_expiration_date(user: User) -> None:
    if user.birth_date is None:
        raise ValueError("User has no birth_date")
    assert user.deposit and user.deposit.expirationDate  # helps mypy

    current_deposit_expiration_datetime = user.deposit.expirationDate
    new_deposit_expiration_datetime = compute_underage_deposit_expiration_datetime(user.birth_date)  # type: ignore [arg-type]

    if current_deposit_expiration_datetime == new_deposit_expiration_datetime:
        return

    logger.info(
        "Updating deposit expiration date for underage beneficiary %s",
        user.id,
        extra={
            "user": user.id,
            "deposit": user.deposit.id,
            "current_expiration_date": current_deposit_expiration_datetime,
            "new_expiration_date": new_deposit_expiration_datetime,
        },
    )

    if new_deposit_expiration_datetime > datetime.datetime.utcnow():
        user.deposit.expirationDate = new_deposit_expiration_datetime
    else:
        if current_deposit_expiration_datetime < datetime.datetime.utcnow():
            # no need to update the deposit expirationDate because it is already passed
            return
        # Else, reduce to now and not to the theoretical new date in case there are bookings made between these dates
        user.deposit.expirationDate = datetime.datetime.utcnow()

    repository.save(user.deposit)


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
        "validatedBirthDate",
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
        "dateCreated",
        "validatedBirthDate",
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
        "recreditAmountToShow",
        "roles",
        "suspension_history",
    ]

    column_labels = dict(
        comment="Commentaire",
        validatedBirthDate="Date de naissance (validée)",
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
        suspension_history="Historique de suspension",
        total_remaining="Crédit global restant",
        total_initial="Crédit initial",
    )

    column_searchable_list = ["id", "email", "firstName", "lastName"]
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
    def form_columns(self) -> typing.Tuple:
        fields: typing.Tuple = (
            "email",
            "validatedBirthDate",
            "departementCode",
            "postalCode",
            "phoneNumber",
            "needsToFillCulturalSurvey",
        )
        if self.check_super_admins():
            fields += ("firstName", "lastName", "idPieceNumber", "ineHash", "comment")

        return fields

    form_args = dict(
        firstName=dict(validators=[DataRequired()]),
        lastName=dict(validators=[DataRequired()]),
        validatedBirthDate=dict(validators=[DataRequired()]),
        postalCode=dict(validators=[DataRequired()]),
        email=dict(validators=[DataRequired()], filters=[filter_email]),
        ineHash=dict(label="INE (hash)"),
    )

    def get_create_form(self) -> Form:
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
        if is_created:
            # Necessary because Flask-Admin calls a function of SQLAlchemy
            # that uses __new__, not __init__ (that sets `roles`).
            model.roles = []
            model.add_beneficiary_role()

            users_api.fulfill_beneficiary_data(model, "pass-culture-admin", EligibilityType.AGE18)

        super().on_model_change(form, model, is_created)

    def after_model_change(self, form: Form, model: User, is_created: bool) -> None:
        if _has_underage_deposit(model):
            _update_underage_beneficiary_deposit_expiration_date(model)
        update_external_user(model)
        super().after_model_change(form, model, is_created)

    def get_one(self, model_id: str) -> BaseQuery:
        return User.query.get(tools.iterdecode(model_id))

    def get_query(self) -> BaseQuery:
        return (
            User.query.filter(User.has_pro_role.is_(False))  # type: ignore [attr-defined]
            .filter(User.is_beneficiary.is_(True))  # type: ignore [attr-defined]
            .options(joinedload(User.deposits))
            .options(joinedload(User.action_history))
        )

    def get_count_query(self) -> BaseQuery:
        return (
            self.session.query(func.count("*"))
            .select_from(self.model)
            .filter(User.has_pro_role.is_(False))  # type: ignore [attr-defined]
            .filter(User.has_beneficiary_role.is_(True))  # type: ignore [attr-defined]
        )
