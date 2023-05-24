from datetime import timedelta

from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
import pytz
import sqlalchemy as sa

from pcapi.core.finance import exceptions as finance_exceptions
from pcapi.core.finance import models as finance_models
from pcapi.core.finance import utils as finance_utils
from pcapi.core.finance import validation as finance_validation
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offers import models as offers_models
from pcapi.core.permissions import models as perm_models
from pcapi.models import db
from pcapi.utils import date as date_utils
from pcapi.utils import db as db_utils

from . import autocomplete
from . import utils
from .forms import custom_reimbursement_rule as custom_reimbursement_rule_forms


custom_reimbursement_rules_blueprint = utils.child_backoffice_blueprint(
    "reimbursement_rules",
    __name__,
    url_prefix="/reimbursement-rules",
    permission=perm_models.Permissions.READ_REIMBURSEMENT_RULES,
)


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
            sa.orm.joinedload(finance_models.CustomReimbursementRule.offer)
            .load_only(offers_models.Offer.id, offers_models.Offer.name)
            .joinedload(offers_models.Offer.venue)
            .load_only(
                offerers_models.Venue.name,
                offerers_models.Venue.publicName,
                offerers_models.Venue.isVirtual,
                offerers_models.Venue.managingOffererId,
            )
            .joinedload(offerers_models.Venue.managingOfferer)
            .load_only(
                offerers_models.Offerer.id,
                offerers_models.Offerer.name,
                offerers_models.Offerer.siren,
            ),
        )
    )

    if form.offerer.data:
        # search on offererId for custom rules on offerers, and on offer's offerer id
        # for custom rules on offers
        base_query = base_query.filter(
            sa.or_(
                finance_models.CustomReimbursementRule.offererId.in_(form.offerer.data),
                offerers_models.Offerer.id.in_(form.offerer.data),
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
def list_custom_reimbursement_rules() -> utils.BackofficeResponse:
    form = custom_reimbursement_rule_forms.GetCustomReimbursementRulesListForm(formdata=utils.get_query_params())
    if not form.validate():
        return render_template("custom_reimbursement_rules/list.html", rows=[], form=form), 400

    custom_reimbursement_rules = _get_custom_reimbursement_rules(form)

    if len(custom_reimbursement_rules) > form.limit.data:
        flash(
            f"Il y a plus de {form.limit.data} résultats dans la base de données, la liste ci-dessous n'en donne donc "
            "qu'une partie. Veuillez affiner les filtres de recherche.",
            "info",
        )
        custom_reimbursement_rules = custom_reimbursement_rules[: form.limit.data]

    autocomplete.prefill_offerers_choices(form.offerer)

    return render_template(
        "custom_reimbursement_rules/list.html",
        rows=custom_reimbursement_rules,
        form=form,
    )


@custom_reimbursement_rules_blueprint.route("/create", methods=["POST"])
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

    custom_reimbursement_rule = finance_models.CustomReimbursementRule(
        subcategories=form.subcategories.data,
        offererId=form.offerer.data[0],
        rate=form.rate.data / 100,
        timespan=[start_datetime, end_datetime],
    )

    return _commit_reimbursement_rule(custom_reimbursement_rule, "créé")


@custom_reimbursement_rules_blueprint.route("/new", methods=["GET"])
@utils.permission_required(perm_models.Permissions.CREATE_REIMBURSEMENT_RULES)
def get_create_custom_reimbursement_rule_form() -> utils.BackofficeResponse:
    form = custom_reimbursement_rule_forms.CreateCustomReimbursementRuleForm()

    return render_template(
        "components/turbo/modal_form.html",
        form=form,
        dst=url_for("backoffice_v3_web.reimbursement_rules.create_custom_reimbursement_rule"),
        div_id="create-custom-reimbursement-rule",  # must be consistent with parameter passed to build_lazy_modal
        title="Créer un tarif dérogatoire",
        button_text="Créer le tarif dérogatoire",
    )


@custom_reimbursement_rules_blueprint.route("/<int:reimbursement_rule_id>/edit", methods=["GET"])
@utils.permission_required(perm_models.Permissions.CREATE_REIMBURSEMENT_RULES)
def get_edit_custom_reimbursement_rule_form(reimbursement_rule_id: int) -> utils.BackofficeResponse:
    custom_reimbursement_rule = finance_models.CustomReimbursementRule.query.get_or_404(reimbursement_rule_id)

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
            "backoffice_v3_web.reimbursement_rules.edit_custom_reimbursement_rule",
            reimbursement_rule_id=reimbursement_rule_id,
        ),
        div_id=f"edit-custom-reimbursement-rule-{reimbursement_rule_id}",  # must be consistent with parameter passed to build_lazy_modal
        title="Modifier un tarif dérogatoire",
        button_text="Enregistrer",
    )


@custom_reimbursement_rules_blueprint.route("/<int:reimbursement_rule_id>/edit", methods=["POST"])
@utils.permission_required(perm_models.Permissions.CREATE_REIMBURSEMENT_RULES)
def edit_custom_reimbursement_rule(reimbursement_rule_id: int) -> utils.BackofficeResponse:
    custom_reimbursement_rule = finance_models.CustomReimbursementRule.query.get_or_404(reimbursement_rule_id)

    form = custom_reimbursement_rule_forms.EditCustomReimbursementRuleForm()
    if not form.validate():
        flash(utils.build_form_error_msg(form), "warning")
        return _redirect_after_reimbursement_rule_action()

    start_datetime = custom_reimbursement_rule.timespan.lower
    if form.end_date.data:
        # upper bound is exclusive, so it should be set at 0:00 on the day after
        end_datetime = date_utils.get_day_start(
            form.end_date.data + timedelta(days=1), finance_utils.ACCOUNTING_TIMEZONE
        )
    else:
        end_datetime = None

    custom_reimbursement_rule.timespan = db_utils.make_timerange(start_datetime, end_datetime)
    return _commit_reimbursement_rule(custom_reimbursement_rule, "modifié")


def _commit_reimbursement_rule(
    custom_reimbursement_rule: finance_models.CustomReimbursementRule, verb: str
) -> utils.BackofficeResponse:
    try:
        finance_validation._check_reimbursement_rule_conflicts(custom_reimbursement_rule)
        db.session.add(custom_reimbursement_rule)
        db.session.commit()
    except finance_exceptions.ConflictingReimbursementRule as exp:
        flash(f"Ce tarif dérogatoire est en conflit avec les tarifs dérogatoires {exp.conflicts}", "warning")
    except sa.exc.DataError:
        db.session.rollback()
        flash("La date de fin ne peut être avant la date de début", "warning")
    except sa.exc.IntegrityError as err:
        db.session.rollback()
        flash(f"Tarif dérogatoire non {verb} : {err}", "warning")
    else:
        flash(f"Tarif dérogatoire {verb}", "success")

    return _redirect_after_reimbursement_rule_action()


def _redirect_after_reimbursement_rule_action() -> utils.BackofficeResponse:
    return redirect(request.referrer or url_for("backoffice_v3_web.validation.list_offerers_to_validate"), code=303)
