import datetime
import logging

import flask
import flask_admin
import flask_admin.helpers
import flask_admin.model.helpers
import flask_login
from markupsafe import Markup
import sqlalchemy
import sqlalchemy.orm
import wtforms
import wtforms.validators

from pcapi.admin import base_configuration
from pcapi.connectors.beneficiaries import jouve_backend
import pcapi.core.fraud.api as fraud_api
import pcapi.core.fraud.models as fraud_models
from pcapi.core.subscription import messages as subscription_messages
import pcapi.core.subscription.models as subscription_models
import pcapi.core.users.api as users_api
import pcapi.core.users.models as users_models
from pcapi.domain import user_emails
import pcapi.infrastructure.repository.beneficiary.beneficiary_sql_repository as beneficiary_repository
from pcapi.models import db
from pcapi.models.feature import FeatureToggle


logger = logging.getLogger(__name__)


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


def beneficiary_fraud_review_formatter(view, context, model, name) -> Markup:
    result_mapping_class = {
        fraud_models.FraudReviewStatus.OK: "badge-success",
        fraud_models.FraudReviewStatus.KO: "badge-danger",
        fraud_models.FraudReviewStatus.REDIRECTED_TO_DMS: "badge-secondary",
    }
    if model.beneficiaryFraudReview is None:
        return Markup("""<span class="badge badge-secondary">inconnu</span>""")

    return Markup(
        f"<div><span>{model.beneficiaryFraudReview.author.firstName} {model.beneficiaryFraudReview.author.lastName}</span></div>"
        f"""<span class="badge {result_mapping_class[model.beneficiaryFraudReview.review]}">{model.beneficiaryFraudReview.review.value}</span>"""
    )


def beneficiary_fraud_checks_formatter(view, context, model, name) -> Markup:
    values = []
    for instance in model.beneficiaryFraudChecks:
        values.append(f"<li>{instance.type.value}</li>")

    return Markup(f"""<ul>{"".join(values)}</ul>""")


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

    column_list = [
        "id",
        "firstName",
        "lastName",
        "email",
        "beneficiaryFraudResult",
        "beneficiaryFraudChecks",
        "beneficiaryFraudReview",
        "dateCreated",
    ]
    column_labels = {
        "firstName": "Prénom",
        "lastName": "Nom",
        "beneficiaryFraudResult": "Statut",
        "beneficiaryFraudChecks": "Vérifications anti fraudes",
        "beneficiaryFraudReview": "Evaluation Manuelle",
        "dateCreated": "Date de creation de compte",
    }

    column_searchable_list = ["id", "email", "firstName", "lastName"]
    column_filters = [
        "email",
        "dateCreated",
        "beneficiaryFraudResult.status",
        "beneficiaryFraudChecks.type",
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
    def column_type_formatters(self):
        type_formatters = super().column_type_formatters
        type_formatters[datetime.datetime] = lambda view, value: value.strftime("%d/%m/%Y à %H:%M:%S")
        return type_formatters

    @property
    def column_formatters(self):
        formatters = super().column_formatters
        formatters.update(
            {
                "beneficiaryFraudChecks": beneficiary_fraud_checks_formatter,
                "beneficiaryFraudResult": beneficiary_fraud_result_formatter,
                "beneficiaryFraudReview": beneficiary_fraud_review_formatter,
            }
        )
        return formatters

    def is_accessible(self) -> bool:
        # TODO: remove when we have a clean way to get groups from google.
        # This is a hackish way to filter from a user role which is weak : we do want a way
        # to add permissions based on groups and sync'ed from our google IDP, and not developp a way to do it here.
        if flask_login.current_user.is_authenticated and flask_login.current_user.has_jouve_role:
            return True

        return super().is_accessible()

    def get_query(self):
        filters = users_models.User.beneficiaryFraudChecks.any() | users_models.User.beneficiaryFraudResult.has()
        if flask_login.current_user.has_jouve_role:
            filters = users_models.User.has_beneficiary_role.is_(False) & users_models.User.beneficiaryFraudChecks.any(
                type=fraud_models.FraudCheckType.JOUVE
            )

        query = users_models.User.query.filter(filters).options(
            sqlalchemy.orm.joinedload(users_models.User.beneficiaryFraudChecks),
            sqlalchemy.orm.joinedload(users_models.User.beneficiaryFraudResult),
            sqlalchemy.orm.joinedload(users_models.User.beneficiaryFraudReview),
        )
        return query

    def get_count_query(self):
        filters = users_models.User.beneficiaryFraudChecks.any() | users_models.User.beneficiaryFraudResult.has()
        if flask_login.current_user.has_jouve_role:
            filters = users_models.User.beneficiaryFraudChecks.any(type=fraud_models.FraudCheckType.JOUVE)

        query = db.session.query(sqlalchemy.func.count(users_models.User.id)).filter(filters)
        return query

    @flask_admin.expose("/details/")
    def details_view(self):
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

        return self.render(
            template,
            model=user,
            details_columns=self._details_columns,
            get_value=self.get_detail_value,
            return_url=return_url,
            has_passed_id_check=fraud_api.has_user_passed_fraud_checks(user),
        )

    @flask_admin.expose("/validate/beneficiary/<user_id>", methods=["POST"])
    def validate_beneficiary(self, user_id):
        if not FeatureToggle.BENEFICIARY_VALIDATION_AFTER_FRAUD_CHECKS.is_active():
            flask.flash("Fonctionnalité non activée", "error")
            return flask.redirect(flask.url_for(".details_view", id=user_id))
        if not self.check_super_admins() and not flask_login.current_user.has_jouve_role:
            flask.flash("Vous n'avez pas les droits suffisant pour activer ce bénéficiaire", "error")
            return flask.redirect(flask.url_for(".details_view", id=user_id))
        form = FraudReviewForm(flask.request.form)
        if not form.validate():
            errors = "<br>".join(f"{field}: {error[0]}" for field, error in form.errors.items())
            flask.flash(Markup(f"Erreurs lors de la validation du formulaire: <br> {errors}"), "error")
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
            users_api.update_user_information_from_external_source(user, fraud_api.get_source_data(user))
            users_api.activate_beneficiary(user, "fraud_validation")
            user_emails.send_accepted_as_beneficiary_email(user=user)
            flask.flash(f"L'utilisateur à été activé comme bénéficiaire {user.firstName} {user.lastName}")

        elif review.review == fraud_models.FraudReviewStatus.REDIRECTED_TO_DMS.value:
            review.reason += " ; Redirigé vers DMS"
            user_emails.send_document_verification_error_email(user.email, "unread-document")
            flask.flash(f"L'utilisateur {user.firstName} {user.lastName} à été redirigé vers DMS")
        elif review.review == fraud_models.FraudReviewStatus.KO.value:
            subscription_messages.on_fraud_review_ko(user)
        db.session.add(review)
        db.session.commit()

        flask.flash(f"Une revue manuelle ajoutée pour le bénéficiaire {user.firstName} {user.lastName}")
        return flask.redirect(flask.url_for(".details_view", id=user_id))

    @flask_admin.expose("/update/beneficiary/id_piece_number/<user_id>", methods=["POST"])
    def update_beneficiary_id_piece_number(self, user_id):
        if not self.check_super_admins() and not flask_login.current_user.has_jouve_role:
            flask.flash("Vous n'avez pas les droits suffisant pour activer ce bénéficiaire", "error")
            return flask.redirect(flask.url_for(".details_view", id=user_id))

        form = IDPieceNumberForm(flask.request.form)
        if not form.validate():
            errors = "<br>".join(f"{field}: {error[0]}" for field, error in form.errors.items())
            flask.flash(Markup(f"Erreurs lors de la validation du formulaire: <br> {errors}"), "error")
            return flask.redirect(flask.url_for(".details_view", id=user_id))

        user = users_models.User.query.get(user_id)
        if not user:
            flask.flash("Cet utilisateur n'existe pas", "error")
            return flask.redirect(flask.url_for(".index_view"))
        if user.isBeneficiary:
            flask.flash(f"L'utilisateur {user.id} {user.firstName} {user.lastName} est déjà bénéficiaire")
            return flask.redirect(flask.url_for(".details_view", id=user_id))
        fraud_check = fraud_api.admin_update_identity_fraud_check_result(user, form.data["id_piece_number"])
        if not fraud_check:
            flask.flash("Aucune vérification de fraude disponible", "error")
            return flask.redirect(flask.url_for(".details_view", id=user_id))
        db.session.refresh(user)
        fraud_result = fraud_api.on_identity_fraud_check_result(user, fraud_check)
        if fraud_result.status == fraud_models.FraudStatus.OK:
            # todo : cleanup to use fraud validation journey v2
            if fraud_check.type == fraud_models.FraudCheckType.JOUVE:
                pre_subscription = jouve_backend.get_subscription_from_content(fraud_check.source_data())
            elif fraud_check.type == fraud_models.FraudCheckType.DMS:
                pre_subscription = subscription_models.BeneficiaryPreSubscription.from_dms_source(
                    fraud_check.source_data()
                )
            beneficiary_repository.BeneficiarySQLRepository.save(pre_subscription, user)

        flask.flash(f"N° de pièce d'identitée modifiée sur le bénéficiaire {user.firstName} {user.lastName}")
        return flask.redirect(flask.url_for(".details_view", id=user_id))

    @flask_admin.expose("/validate/beneficiary/phone_number/<user_id>", methods=["POST"])
    def validate_phone_number(self, user_id):
        if not flask_login.current_user.has_admin_role:
            flask.flash(
                "Vous n'avez pas les droits suffisant pour valider le numéro de téléphone de cet utilisateur", "error"
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
