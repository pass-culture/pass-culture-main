from datetime import datetime
from datetime import timedelta
from decimal import Decimal

from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from markupsafe import Markup
import pytz
import sqlalchemy as sa
from werkzeug.exceptions import NotFound

from pcapi.core.categories import subcategories_v2
from pcapi.core.finance import api as finance_api
from pcapi.core.finance import exceptions as finance_exceptions
from pcapi.core.finance import models as finance_models
from pcapi.core.finance import utils as finance_utils
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offers import models as offers_models
from pcapi.core.permissions import models as perm_models
from pcapi.models import db
from pcapi.repository import atomic
from pcapi.repository import mark_transaction_as_invalid
from pcapi.routes.backoffice import autocomplete
from pcapi.routes.backoffice import utils
from pcapi.utils import date as date_utils

from . import forms as custom_reimbursement_rule_forms


custom_reimbursement_rules_blueprint = utils.child_backoffice_blueprint(
    "reimbursement_rules",
    __name__,
    url_prefix="/reimbursement-rules",
    permission=perm_models.Permissions.READ_REIMBURSEMENT_RULES,
)


def get_error_message(exception: Exception) -> str:
    if isinstance(exception, finance_exceptions.ConflictingReimbursementRule):
        msg = str(exception)
        msg += " Identifiant(s) technique(s) : "
        msg += ", ".join(str(rule_id) for rule_id in exception.conflicts)
        msg += "."
        return Markup(msg)  # pylint: disable=markupsafe-uncontrolled-string
    return str(exception)


def _get_custom_reimbursement_rules(
    form: custom_reimbursement_rule_forms.GetCustomReimbursementRulesListForm,
) -> list[finance_models.CustomReimbursementRule]:
    base_query = (
        finance_models.CustomReimbursementRule.query.outerjoin(offers_models.Offer)
        .outerjoin(offerers_models.Venue)
        .outerjoin(offerers_models.Offerer, offerers_models.Venue.managingOfferer)
        .options(
            sa.orm.joinedload(finance_models.CustomReimbursementRule.offerer).load_only(
                offerers_models.Offerer.id,
                offerers_models.Offerer.name,
                offerers_models.Offerer.siren,
            ),
            sa.orm.joinedload(finance_models.CustomReimbursementRule.venue)
            .load_only(
                offerers_models.Venue.id,
                offerers_models.Venue.name,
                offerers_models.Venue.publicName,
                offerers_models.Venue.isVirtual,
                offerers_models.Venue.managingOffererId,
                offerers_models.Venue.siret,
            )
            .joinedload(offerers_models.Venue.managingOfferer)
            .load_only(
                offerers_models.Offerer.id,
                offerers_models.Offerer.name,
                offerers_models.Offerer.siren,
            ),
            sa.orm.joinedload(finance_models.CustomReimbursementRule.offer)
            .load_only(offers_models.Offer.id, offers_models.Offer.name)
            .joinedload(offers_models.Offer.venue)
            .load_only(
                offerers_models.Venue.name,
                offerers_models.Venue.publicName,
                offerers_models.Venue.isVirtual,
                offerers_models.Venue.managingOffererId,
                offerers_models.Venue.siret,
            )
            .joinedload(offerers_models.Venue.managingOfferer)
            .load_only(
                offerers_models.Offerer.id,
                offerers_models.Offerer.name,
                offerers_models.Offerer.siren,
            ),
        )
    )

    if form.venue.data:
        # search on venueId for custom rules on venues, and on offer's venue id
        # for custom rules on offers
        base_query = base_query.filter(
            sa.or_(
                finance_models.CustomReimbursementRule.venueId.in_(form.venue.data),
                offerers_models.Venue.id.in_(form.venue.data),
            )
        )

    if form.offerer.data:
        # search on offererId for custom rules on offerers, on offer's venue's offerer id
        # for custom rules on venues and on offer's offerer id for custom rules on offers
        base_query = base_query.filter(
            sa.or_(
                finance_models.CustomReimbursementRule.offererId.in_(form.offerer.data),
                offerers_models.Venue.managingOffererId.in_(form.offerer.data),
                offerers_models.Offerer.id.in_(form.offerer.data),
            )
        )

    if form.subcategories.data:
        base_query = base_query.filter(
            finance_models.CustomReimbursementRule.subcategories.overlap(
                sa.dialects.postgresql.array(form.subcategories.data)
            )
        )

    if form.categories.data:
        base_query = base_query.filter(
            finance_models.CustomReimbursementRule.subcategories.overlap(
                sa.dialects.postgresql.array(
                    [
                        subcategory.id
                        for subcategory in subcategories_v2.ALL_SUBCATEGORIES
                        if subcategory.category.id in form.categories.data
                    ]
                )
            )
        )

    if form.q.data:
        search_query = form.q.data

        if search_query.isnumeric():
            query = base_query.filter(offers_models.Offer.id == int(search_query))

        else:
            name = "%{}%".format(search_query)
            query = base_query.filter(offers_models.Offer.name.ilike(name))
    else:
        query = base_query

    # +1 to check if there are more results than requested
    return query.limit(form.limit.data + 1).all()


@custom_reimbursement_rules_blueprint.route("", methods=["GET"])
@atomic()
def list_custom_reimbursement_rules() -> utils.BackofficeResponse:
    form = custom_reimbursement_rule_forms.GetCustomReimbursementRulesListForm(formdata=utils.get_query_params())
    if not form.validate():
        return render_template("custom_reimbursement_rules/list.html", rows=[], form=form), 400

    custom_reimbursement_rules = _get_custom_reimbursement_rules(form)

    custom_reimbursement_rules = utils.limit_rows(custom_reimbursement_rules, form.limit.data)

    autocomplete.prefill_offerers_choices(form.offerer)
    autocomplete.prefill_venues_choices(form.venue, only_with_siret=True)

    return render_template(
        "custom_reimbursement_rules/list.html",
        rows=custom_reimbursement_rules,
        form=form,
        now=datetime.utcnow(),
    )


def _get_custom_reimburement_rule_stats() -> dict[str, int]:
    query = sa.select(sa.func.jsonb_object_agg(sa.text("rule_group"), sa.text("number"))).select_from(
        sa.select(
            sa.case(
                (finance_models.CustomReimbursementRule.offerId.is_not(None), "by_offer"),
                (finance_models.CustomReimbursementRule.offererId.is_not(None), "by_offerer"),
                (finance_models.CustomReimbursementRule.venueId.is_not(None), "by_venue"),
            ).label("rule_group"),
            sa.func.count(finance_models.CustomReimbursementRule.id).label("number"),
        )
        .group_by("rule_group")
        .subquery()
    )
    (data,) = db.session.execute(query).one()

    return data


@custom_reimbursement_rules_blueprint.route("/stats", methods=["GET"])
@atomic()
def get_stats() -> utils.BackofficeResponse:
    stats = _get_custom_reimburement_rule_stats()

    return render_template(
        "custom_reimbursement_rules/list/stats.html",
        stats=stats,
    )


@custom_reimbursement_rules_blueprint.route("/create", methods=["POST"])
@atomic()
@utils.permission_required(perm_models.Permissions.CREATE_REIMBURSEMENT_RULES)
def create_custom_reimbursement_rule() -> utils.BackofficeResponse:
    form = custom_reimbursement_rule_forms.CreateCustomReimbursementRuleForm()
    if not form.validate():
        flash(utils.build_form_error_msg(form), "warning")
        return _redirect_after_reimbursement_rule_action()

    start_datetime = date_utils.get_day_start(form.start_date.data, finance_utils.ACCOUNTING_TIMEZONE)
    if form.end_date.data:
        # upper bound is exclusive, so it should be set at 0:00 on the day after
        end_datetime = date_utils.get_day_start(
            form.end_date.data + timedelta(days=1), finance_utils.ACCOUNTING_TIMEZONE
        )
    else:
        end_datetime = None

    rate = Decimal(form.rate.data / 100).quantize(Decimal("0.0001"))

    try:
        if form.offerer.data[0]:
            finance_api.create_offerer_reimbursement_rule(
                offerer_id=int(form.offerer.data[0]),
                subcategories=form.subcategories.data,
                rate=rate,
                start_date=start_datetime,
                end_date=end_datetime,
            )
        else:  # if it's not an offerer rule, then it's a venue one
            finance_api.create_venue_reimbursement_rule(
                venue_id=int(form.venue.data[0]),
                subcategories=form.subcategories.data,
                rate=rate,
                start_date=start_datetime,
                end_date=end_datetime,
            )
    except (ValueError, finance_exceptions.ReimbursementRuleValidationError) as exc:
        flash(get_error_message(exc), "warning")
    except sa.exc.IntegrityError as err:
        mark_transaction_as_invalid()
        flash(Markup("Une erreur s'est produite : {message}").format(message=str(err)), "warning")
    else:
        flash("Le nouveau tarif dérogatoire a été créé", "success")

    return _redirect_after_reimbursement_rule_action()


@custom_reimbursement_rules_blueprint.route("/new", methods=["GET"])
@atomic()
@utils.permission_required(perm_models.Permissions.CREATE_REIMBURSEMENT_RULES)
def get_create_custom_reimbursement_rule_form() -> utils.BackofficeResponse:
    form = custom_reimbursement_rule_forms.CreateCustomReimbursementRuleForm()

    return render_template(
        "components/turbo/modal_form.html",
        form=form,
        dst=url_for("backoffice_web.reimbursement_rules.create_custom_reimbursement_rule"),
        div_id="create-custom-reimbursement-rule",  # must be consistent with parameter passed to build_lazy_modal
        title="Créer un tarif dérogatoire",
        button_text="Créer le tarif dérogatoire",
    )


@custom_reimbursement_rules_blueprint.route("/<int:reimbursement_rule_id>/edit", methods=["GET"])
@atomic()
@utils.permission_required(perm_models.Permissions.CREATE_REIMBURSEMENT_RULES)
def get_edit_custom_reimbursement_rule_form(reimbursement_rule_id: int) -> utils.BackofficeResponse:
    custom_reimbursement_rule = finance_models.CustomReimbursementRule.query.filter_by(
        id=reimbursement_rule_id
    ).one_or_none()
    if not custom_reimbursement_rule:
        raise NotFound()

    # upper bound is exclusive, and we want to show the last day included in the date range
    end_datetime = custom_reimbursement_rule.timespan.upper
    if end_datetime:
        end_datetime = pytz.utc.localize(end_datetime - timedelta(microseconds=1)).astimezone(
            finance_utils.ACCOUNTING_TIMEZONE
        )

    form = custom_reimbursement_rule_forms.EditCustomReimbursementRuleForm(
        end_date=end_datetime.date().isoformat() if end_datetime else None
    )

    return render_template(
        "components/turbo/modal_form.html",
        form=form,
        dst=url_for(
            "backoffice_web.reimbursement_rules.edit_custom_reimbursement_rule",
            reimbursement_rule_id=reimbursement_rule_id,
        ),
        div_id=f"edit-custom-reimbursement-rule-{reimbursement_rule_id}",  # must be consistent with parameter passed to build_lazy_modal
        title="Modifier un tarif dérogatoire",
        button_text="Enregistrer",
    )


@custom_reimbursement_rules_blueprint.route("/<int:reimbursement_rule_id>/edit", methods=["POST"])
@atomic()
@utils.permission_required(perm_models.Permissions.CREATE_REIMBURSEMENT_RULES)
def edit_custom_reimbursement_rule(reimbursement_rule_id: int) -> utils.BackofficeResponse:
    custom_reimbursement_rule = finance_models.CustomReimbursementRule.query.filter_by(
        id=reimbursement_rule_id
    ).one_or_none()
    if not custom_reimbursement_rule:
        raise NotFound()

    form = custom_reimbursement_rule_forms.EditCustomReimbursementRuleForm()
    if not form.validate():
        flash(utils.build_form_error_msg(form), "warning")
        return _redirect_after_reimbursement_rule_action()

    # upper bound is exclusive, so it should be set at 0:00 on the day after
    end_datetime = date_utils.get_day_start(form.end_date.data + timedelta(days=1), finance_utils.ACCOUNTING_TIMEZONE)

    try:
        finance_api.edit_reimbursement_rule(custom_reimbursement_rule, end_date=end_datetime)
    except (ValueError, finance_exceptions.ReimbursementRuleValidationError) as exc:
        flash(get_error_message(exc), "warning")
    except sa.exc.IntegrityError as err:
        mark_transaction_as_invalid()
        flash(Markup("Une erreur s'est produite : {message}").format(message=str(err)), "warning")
    else:
        flash("Le tarif dérogatoire a été mis à jour", "success")

    return _redirect_after_reimbursement_rule_action()


def _redirect_after_reimbursement_rule_action() -> utils.BackofficeResponse:
    return redirect(request.referrer or url_for("backoffice_web.validation.list_offerers_to_validate"), code=303)
