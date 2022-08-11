import collections
import datetime
from decimal import Decimal
import typing

from flask_admin.form import SecureForm
from flask_login import current_user
from jinja2.runtime import Context
import markupsafe
import pytz
from sqlalchemy.orm import Query
from sqlalchemy.orm import joinedload
from werkzeug.exceptions import Forbidden
import wtforms.fields as wtf_fields
import wtforms.validators as wtf_validators

from pcapi.admin import fields
from pcapi.admin import permissions
from pcapi.admin import widgets
from pcapi.admin.base_configuration import BaseAdminView
from pcapi.core.categories.categories import ALL_CATEGORIES_DICT
from pcapi.core.categories.subcategories import ALL_SUBCATEGORIES
from pcapi.core.categories.subcategories import ALL_SUBCATEGORIES_DICT
import pcapi.core.finance.utils as finance_utils
import pcapi.core.offerers.models as offerers_models
import pcapi.core.offers.models as offers_models
import pcapi.core.payments.api as payments_api
import pcapi.core.payments.exceptions as payments_exceptions
import pcapi.core.payments.models as payment_models
import pcapi.utils.date as date_utils
from pcapi.utils.mailing import build_pc_pro_offer_link
from pcapi.utils.mailing import build_pc_pro_offerer_link
from pcapi.utils.mailing import build_pc_pro_venue_link


def _get_subcategory_choices() -> list[tuple[str, list[tuple[str, str]]]]:
    choices = collections.defaultdict(list)
    for subcategory in ALL_SUBCATEGORIES:
        if subcategory.is_selectable:
            choices[ALL_CATEGORIES_DICT[subcategory.category_id].pro_label].append(
                (subcategory.id, subcategory.pro_label)
            )

    return sorted((category_label, sorted(options, key=lambda o: o[1])) for category_label, options in choices.items())


SUBCATEGORY_CHOICES = _get_subcategory_choices()


def get_offerers(offerer_ids: list) -> list[dict[str, str]]:
    return [
        {"id": str(offerer.id), "text": offerer.name}
        for offerer in offerers_models.Offerer.query.filter(offerers_models.Offerer.id.in_(offerer_ids))
    ]


class AddForm(SecureForm):
    class Meta(SecureForm.Meta):
        # Specify locale to use the comma as the decimal separator for
        # the `rate` field.
        locales = ["fr"]

    offerer = wtf_fields.StringField(
        "Offreur",
        validators=[wtf_validators.DataRequired()],
        widget=widgets.AutocompleteSelectWidget(endpoint="/pc/back-office/autocomplete/offerers", getter=get_offerers),
    )
    subcategories = fields.SelectMultipleFieldWithOptgroups(
        "Sous-catégories",
        description="Laissez vide si toutes les sous-catégories sont concernées ; sélectionnez les sous-catégories souhaitées sinon. Pour sélectionner plusieurs sous-catégories, gardez appuyées les touches &lt;Cmd&gt; et/ou &lt;Majuscule&gt; sur Mac, et les touches &lt;Ctrl&gt; et/ou &lt;majuscule&gt; sur PC.",
        size=10,
        choices=SUBCATEGORY_CHOICES,
    )
    rate = wtf_fields.DecimalField(
        "Taux de remboursement (%)",
        description="Un taux de remboursement (en pourcentage), compris entre 0 et 100. "
        'Par exemple, pour 95 %, saisir "95". Pour 88,23 %, saisir "88,23".',
        use_locale=True,
        validators=[
            wtf_validators.DataRequired(),
            wtf_validators.NumberRange(0, 100, message="Le taux doit être compris entre %(min)s et %(max)s."),
        ],
    )
    start_date = wtf_fields.DateField(
        "Date de début d'application",
        description="Cette date ne peut pas être antérieure à demain.",
        validators=[wtf_validators.DataRequired()],
        widget=widgets.DateInputWithConstraint(
            min_date=lambda _field: datetime.date.today() + datetime.timedelta(days=1)
        ),
    )
    end_date = wtf_fields.DateField(
        "Date de fin d'application (optionnelle)",
        validators=[wtf_validators.Optional()],
        widget=widgets.DateInputWithConstraint(
            min_date=lambda _field: datetime.date.today() + datetime.timedelta(days=2)
        ),
    )


class EditForm(SecureForm):
    end_date = wtf_fields.DateField(
        "Date de fin d'application",
        validators=[wtf_validators.DataRequired()],
        widget=widgets.DateInputWithConstraint(
            min_date=lambda _field: datetime.date.today() + datetime.timedelta(days=1)
        ),
    )


def format_amount(
    view: BaseAdminView, context: Context, model: payment_models.CustomReimbursementRule, name: str
) -> str:
    if not model.amount:
        return ""
    return f"{model.amount} €".replace(".", ",")


def format_offer(
    view: BaseAdminView, context: Context, model: payment_models.CustomReimbursementRule, name: str
) -> str:
    if not model.offer:
        return ""
    url = build_pc_pro_offer_link(model.offer)
    return markupsafe.Markup('<a href="{url}">{offer.name} ({offer.id})</a>').format(
        url=url,
        offer=model.offer,
    )


def format_offerer(
    view: BaseAdminView, context: Context, model: payment_models.CustomReimbursementRule, name: str
) -> str:
    offerer = model.offerer or model.offer.venue.managingOfferer
    url = build_pc_pro_offerer_link(offerer)
    return markupsafe.Markup('<a href="{url}">{offerer.name}</a>').format(
        url=url,
        offerer=offerer,
    )


def format_rate(view: BaseAdminView, context: Context, model: payment_models.CustomReimbursementRule, name: str) -> str:
    if not model.rate:
        return ""
    return f"{model.rate * 100:.2f} %".replace(".", ",")


def format_timespan(
    view: BaseAdminView, context: Context, model: payment_models.CustomReimbursementRule, name: str
) -> str:
    if not model.timespan:
        return ""
    start = pytz.utc.localize(model.timespan.lower).astimezone(finance_utils.ACCOUNTING_TIMEZONE).strftime("%d/%m/%Y")
    if model.timespan.upper:
        end = pytz.utc.localize(model.timespan.upper).astimezone(finance_utils.ACCOUNTING_TIMEZONE).strftime("%d/%m/%Y")
    else:
        end = "∞"
    return markupsafe.Markup("{start} → {end}").format(start=start, end=end)


def format_subcategories(
    view: BaseAdminView, context: Context, model: payment_models.CustomReimbursementRule, name: str
) -> str:
    if not model.subcategories:
        return ""
    labels = sorted(ALL_SUBCATEGORIES_DICT[subcategory_id].pro_label for subcategory_id in model.subcategories)
    if model.offererId and not labels:
        return "toutes les sous-catégories"
    if len(labels) > 5:
        summary = ", ".join(labels)
        displayed_labels = ", ".join(labels[:5])
        return markupsafe.Markup('<span title="{summary}">{labels}, &hellip;</span>').format(
            summary=summary, labels=displayed_labels
        )
    displayed_labels = ", ".join(labels)
    return markupsafe.Markup(displayed_labels)  # pylint: disable=markupsafe-uncontrolled-string


def format_siren(
    view: BaseAdminView, context: Context, model: payment_models.CustomReimbursementRule, name: str
) -> str:
    offerer = model.offerer or model.offer.venue.managingOfferer
    return offerer.siren


def format_venue(
    view: BaseAdminView, context: Context, model: payment_models.CustomReimbursementRule, name: str
) -> str:
    if model.offererId:
        return ""
    venue = model.offer.venue
    url = build_pc_pro_venue_link(venue)
    return markupsafe.Markup('<a href="{url}">{name}</a>').format(
        url=url,
        name=venue.publicName or venue.name,
    )


def get_error_message(exception: payments_exceptions.ReimbursementRuleValidationError) -> str:
    if isinstance(exception, payments_exceptions.ConflictingReimbursementRule):
        msg = str(exception)
        msg += " Identifiant(s) technique(s) : "
        msg += ", ".join(
            f'<a href="/pc/back-office/customreimbursementrule/?flt1_0={rule_id}" target="_blank">{rule_id}</a>'
            for rule_id in exception.conflicts
        )
        msg += "."
        return markupsafe.Markup(msg)  # pylint: disable=markupsafe-uncontrolled-string
    return str(exception)


class CustomReimbursementRuleView(BaseAdminView):
    can_delete = False
    column_list = [
        "id",
        "offerer",
        "siren",
        "venue",
        "offer",
        "rate",
        "amount",
        "subcategories",
        "timespan",
    ]
    column_labels = {
        "offerer": "Offreur",
        "siren": "SIREN",
        "venue": "Lieu",
        "offer": "Offre",
        "rate": "Taux de remboursement",
        "amount": "Montant remboursé",
        "subcategories": "Sous-catégories",
        "timespan": "Dates d'application",
    }
    column_formatters = {
        "amount": format_amount,
        "offer": format_offer,
        "offerer": format_offerer,
        "rate": format_rate,
        "siren": format_siren,
        "subcategories": format_subcategories,
        "timespan": format_timespan,
        "venue": format_venue,
    }
    column_filters = ["id", "offerer.name", "offer.name"]

    @property
    def can_create(self) -> bool:  # type: ignore [override]
        return self.can_add_or_modify()

    @property
    def can_edit(self) -> bool:  # type: ignore [override]
        return self.can_add_or_modify()

    def can_add_or_modify(self) -> bool:
        # We don't call `has_permission()` from `is_accessible()`
        # because we still want admin users to be able to list
        # reimbursement rules. We want to restrict addition and
        # modification only.
        return permissions.has_permission(current_user, "add-or-modify-custom-reimbursement-rules")

    def get_query(self) -> Query:
        return self.model.query.options(
            joinedload(self.model.offerer),
            joinedload(self.model.offer)
            .joinedload(offers_models.Offer.venue)
            .joinedload(offerers_models.Venue.managingOfferer),
        )

    def get_create_form(self) -> typing.Type[AddForm]:
        return AddForm

    def get_edit_form(self) -> typing.Type[EditForm]:
        return EditForm

    def create_model(self, form: AddForm) -> payment_models.CustomReimbursementRule | None:
        if not self.can_create:
            raise Forbidden()
        start_date = date_utils.get_day_start(form.start_date.data, finance_utils.ACCOUNTING_TIMEZONE)
        end_date = (
            date_utils.get_day_start(form.end_date.data, finance_utils.ACCOUNTING_TIMEZONE)
            if form.end_date.data
            else None
        )
        rate = Decimal(form.rate.data / 100).quantize(Decimal("0.0001"))
        try:
            rule = payments_api.create_offerer_reimbursement_rule(
                offerer_id=int(form.offerer.data),
                subcategories=form.subcategories.data,
                rate=rate,
                start_date=start_date,
                end_date=end_date,
            )
            return rule
        except payments_exceptions.ReimbursementRuleValidationError as exc:
            # XXX (dbaty, 2021-10-20): WTForms does not have form-level validation, as of 2.3.3.
            # https://github.com/wtforms/wtforms/commit/22636b55eda9300b549c8bbaae6f9ae31595d445
            form._fields["offerer"].errors = [get_error_message(exc)]
            return None

    def update_model(
        self, form: EditForm, rule: payment_models.CustomReimbursementRule
    ) -> payment_models.CustomReimbursementRule | None:
        if not self.can_edit:
            raise Forbidden()
        end_date = date_utils.get_day_start(form.end_date.data, finance_utils.ACCOUNTING_TIMEZONE)
        try:
            rule = payments_api.edit_reimbursement_rule(rule, end_date=end_date)
        except payments_exceptions.ReimbursementRuleValidationError as exc:
            form._fields["end_date"].errors = [get_error_message(exc)]
            return None
        return rule
