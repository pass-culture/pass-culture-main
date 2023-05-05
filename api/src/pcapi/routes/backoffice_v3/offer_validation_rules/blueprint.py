from flask import render_template
from flask import url_for
import sqlalchemy as sa

import pcapi.core.offers.models as offers_models
import pcapi.core.permissions.models as perm_models
import pcapi.core.users.models as users_models
from pcapi.utils.clean_accents import clean_accents

from .. import utils
from .forms import SearchRuleForm


offer_validation_rules_blueprint = utils.child_backoffice_blueprint(
    "offer_validation_rules",
    __name__,
    url_prefix="/offer-validation-rules",
    permission=perm_models.Permissions.FRAUD_ACTIONS,
)


@offer_validation_rules_blueprint.route("", methods=["GET"])
def list_rules() -> utils.BackofficeResponse:
    form = SearchRuleForm(formdata=utils.get_query_params())

    base_query = offers_models.OfferValidationRule.query.outerjoin(offers_models.OfferValidationSubRule).options(
        sa.orm.joinedload(offers_models.OfferValidationRule.latestAuthor).load_only(
            users_models.User.firstName, users_models.User.lastName, users_models.User.email
        )
    )

    if not form.validate():
        return (
            render_template("offer_validation_rules/list_rules.html", rows=[], form=form, dst=url_for(".list_rules")),
            400,
        )

    if form.is_empty():
        return render_template(
            "offer_validation_rules/list_rules.html", rows=base_query.all(), form=form, dst=url_for(".list_rules")
        )

    query = clean_accents(form.q.data.replace(" ", "%").replace("-", "%"))
    rules = base_query.filter(sa.func.unaccent(offers_models.OfferValidationRule.name).ilike(f"%{query}%")).distinct()
    return render_template("offer_validation_rules/list_rules.html", rows=rules, form=form, dst=url_for(".list_rules"))
