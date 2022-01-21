import logging

from markupsafe import Markup

import pcapi.core.fraud.models as fraud_models

from . import api as support_api


logger = logging.getLogger(__name__)


def beneficiary_fraud_review_formatter(view, context, model, name) -> Markup:
    result_mapping_class = {
        fraud_models.FraudReviewStatus.OK: "badge-success",
        fraud_models.FraudReviewStatus.KO: "badge-danger",
        fraud_models.FraudReviewStatus.REDIRECTED_TO_DMS: "badge-secondary",
    }
    if model.beneficiaryFraudReview is None:
        return Markup("""<span class="badge badge-secondary">inconnu</span>""")

    reviewer = model.beneficiaryFraudReview.author
    reviewer_name = f"{reviewer.firstName} {reviewer.lastName}"
    review_result = model.beneficiaryFraudReview.review
    badge = result_mapping_class[review_result]
    return Markup(
        """
          <div><span>{reviewer_name}</span></div>
          <span class="badge {badge}">{review_result_value}</span>
        """
    ).format(reviewer_name=reviewer_name, badge=badge, review_result_value=review_result.value)


def beneficiary_fraud_checks_formatter(view, context, model, name) -> Markup:
    html = Markup("<ul>")
    for instance in model.beneficiaryFraudChecks:
        html += Markup("<li>{instance.type.value}</li>").format(instance=instance)
    html += Markup("</ul>")
    return html


def beneficiary_subscription_status_formatter(view, context, model, name) -> Markup:
    result_mapping_class = {
        support_api.BeneficiaryActivationStatus.OK: {"class": "badge-success", "text": "OK"},
        support_api.BeneficiaryActivationStatus.KO: {"class": "badge-danger", "text": "KO"},
        support_api.BeneficiaryActivationStatus.SUSPICIOUS: {"class": "badge-warning", "text": "SUSPICIOUS"},
        support_api.BeneficiaryActivationStatus.INCOMPLETE: {"class": "badge-info", "text": "INCOMPLETE"},
        support_api.BeneficiaryActivationStatus.NOT_APPLICABLE: {"class": "badge-void", "text": "N/A"},
    }
    status = support_api.get_beneficiary_activation_status(model)

    return Markup("""<span class="badge {badge}">{text}</span>""").format(
        badge=result_mapping_class[status]["class"], text=result_mapping_class[status]["text"]
    )
