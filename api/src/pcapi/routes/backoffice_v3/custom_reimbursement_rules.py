from flask import flash
from flask import render_template
import sqlalchemy as sa

from pcapi.core.finance import models as finance_models
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offers import models as offers_models
from pcapi.core.permissions import models as perm_models

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
