from functools import partial
import typing

from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from flask_login import current_user
from flask_sqlalchemy import Pagination
import pydantic

import pcapi.core.fraud.api as fraud_api
import pcapi.core.fraud.models as fraud_models
from pcapi.core.permissions import models as perm_models
import pcapi.core.subscription.api as subscription_api
from pcapi.core.subscription.phone_validation import api as phone_validation_api
from pcapi.core.subscription.phone_validation import exceptions as phone_validation_exceptions
from pcapi.core.users import api as users_api
from pcapi.core.users import exceptions as users_exceptions
from pcapi.core.users import external as users_external
from pcapi.core.users import models as users_models
import pcapi.core.users.constants as users_constants
import pcapi.core.users.email.update as email_update
import pcapi.core.users.utils as users_utils
from pcapi.models import db
import pcapi.utils.email as email_utils

from . import blueprint
from . import search_utils
from . import utils
from .forms import account as account_forms
from .forms import empty as empty_forms
from .forms import search as search_forms
from .serialization import accounts
from .serialization import search


@blueprint.backoffice_v3_web.route("/public_accounts/search", methods=["GET"])
@utils.permission_required(perm_models.Permissions.SEARCH_PUBLIC_ACCOUNT)
def search_public_accounts() -> utils.Response:
    """
    Renders two search pages: first the one with the search form, then
    the one of the results.
    """
    if not request.args:
        return render_search_template()

    form = search_forms.SearchForm(request.args)
    if not form.validate():
        return render_search_template(form), 400

    try:
        # let pydantic run the more detailed validation and format the
        # form's data in a more user-friendly way
        search_model = search.SearchUserModel(**form.data)
    except pydantic.ValidationError as err:
        for error in err.errors():
            form.add_error_to(typing.cast(str, error["loc"][0]))
        return render_search_template(form), 400

    next_page = partial(
        url_for,
        ".search_public_accounts",
        terms=search_model.terms,
        order_by=search_model.order_by,
        page=search_model.page,
        per_page=search_model.per_page,
    )

    paginated_rows = fetch_rows(search_model)
    next_pages_urls = search_utils.pagination_links(next_page, search_model.page, paginated_rows.pages)

    return render_template(
        "accounts/search_result.html",
        dst=url_for(".search_public_accounts"),
        form=form,
        next_pages_urls=next_pages_urls,
        new_search_url=url_for(".search_public_accounts"),
        get_link_to_detail=get_public_account_link,
        rows=paginated_rows,
        terms=search_model.terms,
        order_by=search_model.order_by,
        per_page=search_model.per_page,
    )


def render_search_template(form: search_forms.SearchForm | None = None) -> str:
    if not form:
        form = search_forms.SearchForm()

    return render_template(
        "accounts/search.html",
        title="Recherche grand public",
        dst=url_for(".search_public_accounts"),
        order_by_options=search.OrderByCols,
        form=form,
    )


@blueprint.backoffice_v3_web.route("/public_accounts/<int:user_id>", methods=["GET"])
@utils.permission_required(perm_models.Permissions.READ_PUBLIC_ACCOUNT)
def get_public_account(user_id: int) -> utils.Response:
    user = users_models.User.query.get_or_404(user_id)
    domains_credit = users_api.get_domains_credit(user) if user.is_beneficiary else None
    history = users_api.public_account_history(user)
    eligibility_history = get_eligibility_history(user)

    return render_template(
        "accounts/get.html",
        user=user,
        credit=domains_credit,
        history=history,
        eligibility_history=eligibility_history,
        resend_email_validation_form=empty_forms.EmptyForm(),
        send_validation_code_form=empty_forms.EmptyForm(),
        manual_validation_form=empty_forms.EmptyForm(),
    )


@blueprint.backoffice_v3_web.route("/public_accounts/<int:user_id>/edit", methods=["GET"])
@utils.permission_required(perm_models.Permissions.MANAGE_PUBLIC_ACCOUNT)
def edit_public_account(user_id: int) -> utils.Response:
    user = users_models.User.query.get_or_404(user_id)
    form = account_forms.EditAccountForm(
        last_name=user.lastName,
        first_name=user.firstName,
        email=user.email,
    )
    dst = url_for(".update_public_account", user_id=user.id)

    return render_template("accounts/edit.html", form=form, dst=dst)


@blueprint.backoffice_v3_web.route("/public_accounts/<int:user_id>", methods=["PATCH"])
@utils.permission_required(perm_models.Permissions.MANAGE_PUBLIC_ACCOUNT)
def update_public_account(user_id: int) -> utils.Response:
    user = users_models.User.query.get_or_404(user_id)

    form = account_forms.EditAccountForm()
    if not form.validate():
        dst = url_for(".update_public_account", user_id=user_id)
        return render_template("accounts/edit.html", form=form, dst=dst), 400

    users_api.update_user_information(
        user,
        first_name=form.first_name.data,
        last_name=form.last_name.data,
    )

    if form.email.data and form.email.data != email_utils.sanitize_email(user.email):
        try:
            email_update.request_email_update_from_admin(user, form.email.data)
        except users_exceptions.EmailExistsError:
            form.email.errors.append("L'email est déjà associé à un autre utilisateur")
            dst = url_for(".update_public_account", user_id=user.id)
            return render_template("accounts/edit.html", form=form, dst=dst), 400

    db.session.commit()
    users_external.update_external_user(user)

    flash("Informations mises à jour", "success")
    return redirect(url_for(".get_public_account", user_id=user_id), code=303)


@blueprint.backoffice_v3_web.route("/public_accounts/<int:user_id>/resend-validation-email", methods=["POST"])
@utils.permission_required(perm_models.Permissions.MANAGE_PUBLIC_ACCOUNT)
def resend_validation_email(user_id: int) -> utils.Response:
    user = users_models.User.query.get_or_404(user_id)

    if user.has_admin_role or user.has_pro_role:
        flash("Cette action n'est pas supportée pour les utilisateurs admin ou pro", "warning")
    elif user.isEmailValidated:
        flash("L'adresse email est déjà validée", "warning")
    else:
        users_api.request_email_confirmation(user)
        flash("Email de validation envoyé", "success")

    return redirect(url_for(".get_public_account", user_id=user_id), code=303)


@blueprint.backoffice_v3_web.route("/public_accounts/<int:user_id>/send-validation-code", methods=["POST"])
@utils.permission_required(perm_models.Permissions.MANAGE_PUBLIC_ACCOUNT)
def send_validation_code(user_id: int) -> utils.Response:
    user = users_models.User.query.get_or_404(user_id)

    if not user.phoneNumber:
        flash("L'utilisateur n'a pas de numéro de téléphone", "warning")
        return redirect(url_for(".get_public_account", user_id=user_id), code=303)

    try:
        phone_validation_api.send_phone_validation_code(
            user,
            user.phoneNumber,
            ignore_limit=True,
        )

    except phone_validation_exceptions.UserPhoneNumberAlreadyValidated:
        flash("Le numéro de téléphone est déjà validé", "warning")

    except phone_validation_exceptions.InvalidPhoneNumber:
        flash("Le numéro de téléphone est invalide", "warning")

    except phone_validation_exceptions.UserAlreadyBeneficiary:
        flash("L'utilisateur est déjà bénéficiaire", "warning")

    except phone_validation_exceptions.UnvalidatedEmail:
        flash("L'email de l'utilisateur n'est pas encore validé", "warning")

    except phone_validation_exceptions.PhoneAlreadyExists:
        flash("Un compte est déjà associé à ce numéro", "warning")

    except phone_validation_exceptions.PhoneVerificationException:
        flash("L'envoi du code a échoué", "warning")

    else:
        flash("Le code a été envoyé", "success")

    return redirect(url_for(".get_public_account", user_id=user_id), code=303)


@blueprint.backoffice_v3_web.route("/public_accounts/<int:user_id>/review", methods=["GET"])
@utils.permission_required(perm_models.Permissions.MANAGE_PUBLIC_ACCOUNT)
def edit_public_account_review(user_id: int) -> utils.Response:
    user = users_models.User.query.get_or_404(user_id)
    form = account_forms.ManualReviewForm()
    return render_template("accounts/edit_review.html", form=form, user=user)


@blueprint.backoffice_v3_web.route("/public_accounts/<int:user_id>/review", methods=["POST"])
@utils.permission_required(perm_models.Permissions.MANAGE_PUBLIC_ACCOUNT)
def review_public_account(user_id: int) -> utils.Response:
    user = users_models.User.query.get_or_404(user_id)

    form = account_forms.ManualReviewForm()
    if not form.validate():
        flash("Les données envoyées comportent des erreurs", "warning")
        return render_template("accounts/edit_review.html", form=form, user=user), 400

    eligibility = None if user.eligibility is None else users_models.EligibilityType[form.eligibility.data]

    try:
        fraud_api.validate_beneficiary(
            user=user,
            reviewer=current_user,
            reason=form.reason.data,
            review=fraud_models.FraudReviewStatus(form.status.data),
            eligibility=eligibility,
        )
    except (fraud_api.FraudCheckError, fraud_api.EligibilityError) as err:
        # `validate_beneficiary` immediately creates some objects that
        # will be considered dirty by SQLA.
        # A rollback is therefore needed to prevent some unexpected
        # objects to be persisted into database.
        db.session.rollback()
        flash(str(err), "warning")
    else:
        flash("Validation réussie", "success")

    return redirect(url_for(".get_public_account", user_id=user_id), code=303)


def fetch_rows(search_model: search.SearchUserModel) -> Pagination:
    return search_utils.fetch_paginated_rows(users_api.search_public_account, search_model)


def get_public_account_link(user_id: int) -> str:
    return url_for(".get_public_account", user_id=user_id)


def get_eligibility_history(user: users_models.User) -> dict[str, accounts.EligibilitySubscriptionHistoryModel]:
    subscriptions = {}
    eligibility_types = []

    subscription_item_methods = [
        subscription_api.get_email_validation_subscription_item,
        subscription_api.get_phone_validation_subscription_item,
        subscription_api.get_user_profiling_subscription_item,
        subscription_api.get_profile_completion_subscription_item,
        subscription_api.get_identity_check_subscription_item,
        subscription_api.get_honor_statement_subscription_item,
    ]

    # Do not show information about eligibility types which are not possible depending on known user age
    if user.birth_date:
        age_at_creation = users_utils.get_age_at_date(user.birth_date, user.dateCreated)
        if age_at_creation <= users_constants.ELIGIBILITY_AGE_18:
            if age_at_creation == users_constants.ELIGIBILITY_AGE_18:
                eligibility_types.append(users_models.EligibilityType.AGE18)
            else:
                eligibility_types.append(users_models.EligibilityType.UNDERAGE)
                age_now = users_utils.get_age_from_birth_date(user.birth_date)
                if age_now >= users_constants.ELIGIBILITY_AGE_18:
                    eligibility_types.append(users_models.EligibilityType.AGE18)
    else:
        # Profile completion step not reached yet; can't guess eligibility, display all
        eligibility_types = list(users_models.EligibilityType)

    for eligibility in eligibility_types:
        subscriptions[eligibility.name] = accounts.EligibilitySubscriptionHistoryModel(
            subscriptionItems=[
                accounts.SubscriptionItemModel.from_orm(method(user, eligibility))
                for method in subscription_item_methods
            ],
            idCheckHistory=[
                accounts.IdCheckItemModel.from_orm(fraud_check)
                for fraud_check in user.beneficiaryFraudChecks
                if fraud_check.eligibilityType == eligibility
            ],
        )

    return subscriptions
