from markupsafe import Markup
import sqlalchemy.orm

from pcapi.admin import base_configuration
import pcapi.core.fraud.models as fraud_models
import pcapi.core.users.models as users_models


def beneficiary_fraud_result_formatter(view, context, model, name) -> Markup:
    result_mapping_class = {
        fraud_models.FraudStatus.OK: "badge-success",
        fraud_models.FraudStatus.KO: "badge-danger",
        fraud_models.FraudStatus.SUSPICIOUS: "badge-warning",
    }

    if model.beneficiaryFraudResult:
        instance = model.beneficiaryFraudResult.status
        return Markup(f"""<span class="badge {result_mapping_class[instance]}">{instance.value}</span>""")
    return Markup("""<span class="badge badge-secondary">Inconnu</span>""")


def beneficiary_fraud_checks_formatter(view, context, model, name) -> Markup:
    values = []
    for instance in model.beneficiaryFraudChecks:
        values.append(f"<li>{instance.type.value}</li>")

    return Markup(f"""<ul>{"".join(values)}</ul>""")


class FraudView(base_configuration.BaseAdminView):

    column_list = ["id", "firstName", "lastName", "beneficiaryFraudResult", "beneficiaryFraudChecks"]
    column_labels = {
        "firstName": "Prénom",
        "lastName": "Nom",
        "beneficiaryFraudResult": "Anti Fraude",
        "beneficiaryFraudChecks": "Vérifications anti fraudes",
    }

    column_searchable_list = ["id", "email", "firstName", "lastName"]
    column_filters = ["postalCode", "email", "beneficiaryFraudResult.status", "beneficiaryFraudChecks.type"]

    can_view_details = True
    details_template = "admin/fraud_details.html"

    @property
    def column_formatters(self):
        formatters = super().column_formatters.copy()
        formatters.update(
            {
                "beneficiaryFraudResult": beneficiary_fraud_result_formatter,
                "beneficiaryFraudChecks": beneficiary_fraud_checks_formatter,
            }
        )
        return formatters

    def get_query(self):
        return users_models.User.query.filter(
            (users_models.User.beneficiaryFraudChecks.any()) | (users_models.User.beneficiaryFraudResult.has())
        ).options(
            sqlalchemy.orm.joinedload(users_models.User.beneficiaryFraudChecks),
            sqlalchemy.orm.joinedload(users_models.User.beneficiaryFraudResult),
        )
