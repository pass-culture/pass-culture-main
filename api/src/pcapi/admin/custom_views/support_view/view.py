import datetime
import logging
from typing import Callable

import flask
import flask_admin
import flask_admin.helpers
import flask_admin.model.helpers
import flask_login
from flask_sqlalchemy import BaseQuery
from markupsafe import Markup
import sqlalchemy
import sqlalchemy.orm
from sqlalchemy.sql import ColumnElement
from werkzeug import Response
import wtforms.validators

from pcapi.admin import base_configuration
import pcapi.core.fraud.api as fraud_api
import pcapi.core.fraud.models as fraud_models
from pcapi.core.mails.transactional.users.subscription_document_error import send_subscription_document_error_email
from pcapi.core.subscription import messages as subscription_messages
import pcapi.core.subscription.api as subscription_api
import pcapi.core.subscription.exceptions as subscription_exceptions
import pcapi.core.users.api as users_api
import pcapi.core.users.models as users_models
from pcapi.models import db
from pcapi.models.beneficiary_import import BeneficiaryImportSources
from pcapi.models.feature import FeatureToggle


logger = logging.getLogger(__name__)

from . import api as support_api
from . import utils as support_utils


class FraudReviewForm(wtforms.Form):
    class Meta:
        locales = ["fr"]

    reason = wtforms.TextAreaField(validators=[wtforms.validators.DataRequired()])
    review = wtforms.SelectField(
        choices=[(item.name, item.value) for item in fraud_models.FraudReviewStatus],
        validators=[wtforms.validators.DataRequired()],
    )


class IDPieceNumberForm(wtforms.Form):
    class Meta:
        locales = ["fr"]

    id_piece_number = wtforms.StringField(
        validators=[wtforms.validators.DataRequired(), wtforms.validators.Length(min=8, max=12)]
    )


class BeneficiaryView(base_configuration.BaseAdminView):
    VIEW_FILTERS = {
        "INTERNAL": sqlalchemy.and_(
            users_models.User.has_admin_role.is_(False),
            users_models.User.has_pro_role.is_(False),
        ),
        "UNFILTERED": False,
    }

    column_list = [
        "id",
        "firstName",
        "lastName",
        "email",
        "subscription_status",
        "beneficiaryFraudChecks",
        "beneficiaryFraudReview",
        "dateCreated",
    ]
    column_labels = {
        "firstName": "Prénom",
        "lastName": "Nom",
        "subscription_status": "Statut",
        "beneficiaryFraudChecks": "Vérifications anti fraudes",
        "beneficiaryFraudReview": "Evaluation Manuelle",
        "dateCreated": "Date de creation de compte",
    }

    column_searchable_list = ["id", "email", "firstName", "lastName"]
    column_filters = [
        "email",
        "dateCreated",
        "beneficiaryFraudChecks.type",
        "beneficiaryFraudChecks.status",
        "beneficiaryFraudReview",
    ]

    column_sortable_list = [
        "dateCreated",
    ]

    can_view_details = True
    details_template = "admin/support_beneficiary_details.html"
    list_template = "admin/support_beneficiary_list.html"

    page_size = 100

    @property
    def column_type_formatters(self) -> dict[type, Callable]:
        type_formatters = super().column_type_formatters
        type_formatters[datetime.datetime] = lambda view, value: value.strftime("%d/%m/%Y à %H:%M:%S")
        return type_formatters

    @property
    def column_formatters(self) -> dict[str, Callable]:
        formatters = super().column_formatters
        formatters.update(
            {
                "subscription_status": support_utils.beneficiary_subscription_status_formatter,
                "beneficiaryFraudChecks": support_utils.beneficiary_fraud_checks_formatter,
                "beneficiaryFraudReview": support_utils.beneficiary_fraud_review_formatter,
            }
        )
        return formatters

    def _are_search_and_filters_empty(self) -> bool:
        view_args = self._get_list_extra_args()
        return (not view_args.search) and (not view_args.filters)

    def get_view_filter(self) -> ColumnElement:
        role = "INTERNAL"
        if self._are_search_and_filters_empty():
            role = "UNFILTERED"
        return self.VIEW_FILTERS[role]

    def get_query(self) -> BaseQuery:
        view_filter = self.get_view_filter()
        query = users_models.User.query.filter(view_filter).options(
            sqlalchemy.orm.joinedload(users_models.User.beneficiaryFraudChecks),
            sqlalchemy.orm.joinedload(users_models.User.beneficiaryFraudReview),
        )
        return query

    def get_count_query(self) -> BaseQuery:
        view_filter = self.get_view_filter()
        return users_models.User.query.filter(view_filter).with_entities(sqlalchemy.func.count(users_models.User.id))

    @flask_admin.expose("/details/")
    def details_view(self) -> Response:
        return_url = flask_admin.helpers.get_redirect_target() or self.get_url(".index_view")

        if not self.can_view_details:
            return flask.redirect(return_url)

        object_id = flask_admin.model.helpers.get_mdict_item_or_list(flask.request.args, "id")
        if object_id is None:
            return flask.redirect(return_url)

        user = self.get_one(object_id)

        if user is None:
            flask.flash(flask_admin.babel.gettext("Record does not exist."), "error")
            return flask.redirect(return_url)

        if self.details_modal and flask.request.args.get("modal"):
            template = self.details_modal_template
        else:
            template = self.details_template

        # We display the BeneficiaryImport section if the necessary data is not available in the user's fraud checks
        # This is the case for older applications that don't have the fraud checks data.
        #
        # TODO: Remove this logic when all the applications have the fraud checks data.
        has_id_check_fraud_checks_with_status = any(
            fraud_check
            for fraud_check in user.beneficiaryFraudChecks
            if fraud_check.type in fraud_models.IDENTITY_CHECK_TYPES and fraud_check.status is not None
        )
        user_beneficiary_imports_sources = [beneficiary_import.source for beneficiary_import in user.beneficiaryImports]
        has_jouve_or_dms_beneficiary_import = (
            BeneficiaryImportSources.demarches_simplifiees.value in user_beneficiary_imports_sources
            or BeneficiaryImportSources.jouve.value in user_beneficiary_imports_sources
        )
        display_beneficiary_imports = has_jouve_or_dms_beneficiary_import and not has_id_check_fraud_checks_with_status
        # End of logic to choose if we display the BeneficiaryImport details or not

        return self.render(
            template,
            model=user,
            details_columns=self._details_columns,
            get_value=self.get_detail_value,
            return_url=return_url,
            has_performed_identity_check=fraud_api.has_user_performed_identity_check(user),
            enum_update_request_value=users_models.EmailHistoryEventTypeEnum.UPDATE_REQUEST.value,
            subscription_items=support_api.get_subscription_items_by_eligibility(user),
            next_subscription_step=subscription_api.get_next_subscription_step(user),
            display_beneficiary_imports=display_beneficiary_imports,
        )

    @flask_admin.expose(
        "/validate/beneficiary/<user_id>", methods=["POST"]
    )  # pylint: disable=too-many-return-statements
    def validate_beneficiary(self, user_id: int) -> Response:
        if not FeatureToggle.BENEFICIARY_VALIDATION_AFTER_FRAUD_CHECKS.is_active():
            flask.flash("Fonctionnalité non activée", "error")
            return flask.redirect(flask.url_for(".details_view", id=user_id))
        if not self.check_super_admins():
            flask.flash("Vous n'avez pas les droits suffisants pour activer ce bénéficiaire", "error")
            return flask.redirect(flask.url_for(".details_view", id=user_id))
        form = FraudReviewForm(flask.request.form)
        if not form.validate():
            errors_html = Markup("Erreurs lors de la validation du formulaire: <br>")
            for field, error in form.errors.items():
                errors_html += Markup("{field}: {error[0]}").format(field=field, error=error)
            flask.flash(errors_html, "error")
            return flask.redirect(flask.url_for(".details_view", id=user_id))
        user = users_models.User.query.get(user_id)
        if not user:
            flask.flash("Cet utilisateur n'existe pas", "error")
            return flask.redirect(flask.url_for(".index_view"))

        if user.beneficiaryFraudReview:
            flask.flash(
                f"Une revue manuelle a déjà été réalisée sur l'utilisateur {user.id} {user.firstName} {user.lastName}"
            )
            return flask.redirect(flask.url_for(".details_view", id=user_id))

        review = fraud_models.BeneficiaryFraudReview(
            user=user, author=flask_login.current_user, reason=form.data["reason"], review=form.data["review"]
        )
        if review.review == fraud_models.FraudReviewStatus.OK.value:
            source_data = fraud_api.get_source_data(user)
            users_api.update_user_information_from_external_source(user, source_data)
            eligibility = fraud_api.decide_eligibility(user, source_data)

            if eligibility is None:
                flask.flash("La date de naissance du dossier indique que l'utilisateur n'est pas éligible", "error")
                return flask.redirect(flask.url_for(".details_view", id=user_id))

            try:
                fraud_check = users_api.get_activable_identity_fraud_check(user)
                if not fraud_check:
                    fraud_check = fraud_models.BeneficiaryFraudCheck(
                        user=user,
                        type=fraud_models.FraudCheckType.JOUVE,
                        status=fraud_models.FraudCheckStatus.OK,
                        reason="Validated by admin",
                        eligibilityType=eligibility,
                        thirdPartyId="admin_validation",
                        resultContent={
                            "id": 0,
                            "registrationDate": datetime.datetime.now().isoformat(),
                        },
                    )

                subscription_api.activate_beneficiary(user, "fraud_validation")
            except subscription_exceptions.CannotUpgradeBeneficiaryRole:
                flask.flash("L'utilisateur est déjà bénéficiaire", "error")
            flask.flash(f"L'utilisateur à été activé comme bénéficiaire {user.firstName} {user.lastName}")

        elif review.review == fraud_models.FraudReviewStatus.REDIRECTED_TO_DMS.value:
            review.reason += " ; Redirigé vers DMS"
            send_subscription_document_error_email(user.email, "unread-document")
            flask.flash(f"L'utilisateur {user.firstName} {user.lastName} à été redirigé vers DMS")
            subscription_messages.on_redirect_to_dms_from_idcheck(user)
        elif review.review == fraud_models.FraudReviewStatus.KO.value:
            subscription_messages.on_fraud_review_ko(user)
        db.session.add(review)
        db.session.commit()

        flask.flash(f"Une revue manuelle ajoutée pour le bénéficiaire {user.firstName} {user.lastName}")
        return flask.redirect(flask.url_for(".details_view", id=user_id))

    @flask_admin.expose("/validate/beneficiary/phone_number/<user_id>", methods=["POST"])
    def validate_phone_number(self, user_id: int) -> Response:
        if not flask_login.current_user.has_admin_role:
            flask.flash(
                "Vous n'avez pas les droits suffisants pour valider le numéro de téléphone de cet utilisateur", "error"
            )
            return flask.redirect(flask.url_for(".details_view", id=user_id))

        user = users_models.User.query.get(user_id)
        if not user:
            flask.flash("Cet utilisateur n'existe pas", "error")
            return flask.redirect(flask.url_for(".index_view"))

        user.phoneValidationStatus = users_models.PhoneValidationStatusType.VALIDATED
        db.session.add(user)
        db.session.commit()
        logger.info("flask-admin: Manual phone validation", extra={"validated_user": user.id})
        flask.flash(f"Le n° de téléphone de l'utilisateur {user.id} {user.firstName} {user.lastName} est validé")
        return flask.redirect(flask.url_for(".details_view", id=user_id))
