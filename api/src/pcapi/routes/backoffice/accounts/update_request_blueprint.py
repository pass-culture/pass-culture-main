import datetime
from functools import partial

import sqlalchemy as sa
import sqlalchemy.orm as sa_orm
from flask import flash
from flask import render_template
from flask import request
from flask import url_for
from flask_login import current_user
from markupsafe import Markup
from sqlalchemy.dialects import postgresql
from werkzeug.exceptions import Forbidden
from werkzeug.exceptions import NotFound

from pcapi import settings
from pcapi.connectors.dms import exceptions as dms_exceptions
from pcapi.connectors.dms import models as dms_models
from pcapi.core.external.attributes import api as external_attributes_api
from pcapi.core.finance import models as finance_models
from pcapi.core.history import api as history_api
from pcapi.core.history import models as history_models
from pcapi.core.mails.transactional.users.personal_data_updated import send_beneficiary_personal_data_updated
from pcapi.core.mails.transactional.users.update_request_ask_for_correction import (
    send_beneficiary_update_request_ask_for_correction,
)
from pcapi.core.mails.transactional.users.update_request_identity_theft import (
    send_beneficiary_update_request_identity_theft,
)
from pcapi.core.permissions import models as perm_models
from pcapi.core.subscription.phone_validation import exceptions as phone_validation_exceptions
from pcapi.core.users import api as users_api
from pcapi.core.users import constants as users_constants
from pcapi.core.users import ds as users_ds
from pcapi.core.users import models as users_models
from pcapi.core.users.email import update as email_update
from pcapi.models import db
from pcapi.routes.backoffice import autocomplete
from pcapi.routes.backoffice import filters
from pcapi.routes.backoffice import search_utils
from pcapi.routes.backoffice import utils
from pcapi.routes.backoffice.forms import empty as empty_forms
from pcapi.routes.backoffice.search_utils import paginate
from pcapi.utils import date as date_utils
from pcapi.utils import email as email_utils
from pcapi.utils import phone_number as phone_number_utils
from pcapi.utils import string as string_utils
from pcapi.utils.clean_accents import clean_accents
from pcapi.utils.transaction_manager import mark_transaction_as_invalid

from . import forms as account_forms


account_update_blueprint = utils.child_backoffice_blueprint(
    "account_update",
    __name__,
    url_prefix="/account-update-requests",
    permission=perm_models.Permissions.MANAGE_ACCOUNT_UPDATE_REQUEST,
)


def _get_account_update_requests_query() -> sa_orm.Query:
    aliased_instructor = sa_orm.aliased(users_models.User)
    return (
        db.session.query(users_models.UserAccountUpdateRequest)
        .outerjoin(users_models.User, users_models.UserAccountUpdateRequest.userId == users_models.User.id)
        .outerjoin(
            finance_models.Deposit,
            sa.and_(
                finance_models.Deposit.userId == users_models.User.id,
                finance_models.Deposit.expirationDate > date_utils.get_naive_utc_now(),
            ),
        )
        .outerjoin(aliased_instructor, users_models.UserAccountUpdateRequest.lastInstructorId == aliased_instructor.id)
        .options(
            sa_orm.contains_eager(users_models.UserAccountUpdateRequest.user).load_only(
                users_models.User.id,
                users_models.User.firstName,
                users_models.User.lastName,
                users_models.User.email,
                users_models.User._phoneNumber,
                users_models.User.dateOfBirth,
                users_models.User.validatedBirthDate,
                users_models.User.departementCode,
                users_models.User.civility,
                users_models.User.roles,
            ),
            sa_orm.contains_eager(
                users_models.UserAccountUpdateRequest.lastInstructor.of_type(aliased_instructor)
            ).load_only(
                aliased_instructor.id,
                aliased_instructor.email,
                aliased_instructor.firstName,
                aliased_instructor.lastName,
            ),
            sa_orm.contains_eager(users_models.UserAccountUpdateRequest.user).contains_eager(
                users_models.User.deposits
            ),
        )
    )


def _get_filtered_account_update_requests(form: account_forms.AccountUpdateRequestSearchForm) -> sa_orm.Query:
    query = _get_account_update_requests_query()

    filters = []

    if form.q.data:
        search_query = form.q.data
        term_filters: list[sa.sql.ColumnElement] = []

        # phone number
        try:
            parsed_phone_number = phone_number_utils.parse_phone_number(search_query)
            term_as_phone_number = phone_number_utils.get_formatted_phone_number(parsed_phone_number)
        except phone_validation_exceptions.InvalidPhoneNumber:
            pass  # term can't be a phone number
        else:
            term_filters.append(
                sa.or_(
                    users_models.User.phoneNumber == term_as_phone_number,
                    users_models.UserAccountUpdateRequest.newPhoneNumber == term_as_phone_number,
                )
            )

        # numeric
        if string_utils.is_numeric(search_query):
            term_filters.append(
                sa.or_(
                    users_models.UserAccountUpdateRequest.userId == search_query,
                    users_models.UserAccountUpdateRequest.dsApplicationId == search_query,
                )
            )

        # email
        if email_utils.is_valid_email(search_query):
            term_filters.append(
                sa.or_(
                    users_models.UserAccountUpdateRequest.email == search_query,
                    users_models.UserAccountUpdateRequest.oldEmail == search_query,
                    users_models.UserAccountUpdateRequest.newEmail == search_query,
                    users_models.User.email == search_query,
                )
            )

        # name
        if not term_filters:
            for name in search_query.split():
                search_term = f"%{clean_accents(name)}%"
                term_filters.append(
                    sa.or_(
                        *(
                            sa.func.immutable_unaccent(expression).ilike(search_term)
                            for expression in (
                                sa.func.coalesce(users_models.UserAccountUpdateRequest.firstName, "")
                                + " "
                                + sa.func.coalesce(users_models.UserAccountUpdateRequest.newFirstName, "")
                                + " "
                                + sa.func.coalesce(users_models.UserAccountUpdateRequest.lastName, "")
                                + " "
                                + sa.func.coalesce(users_models.UserAccountUpdateRequest.newLastName, ""),
                                users_models.User.firstName + " " + users_models.User.lastName,
                            )
                        )
                    )
                )
            filters.append(sa.and_(*term_filters) if len(term_filters) > 1 else term_filters[0])

        else:
            filters.append(sa.or_(*term_filters) if len(term_filters) > 1 else term_filters[0])

    if form.from_to_date.data:
        if form.from_to_date.from_date is not None and form.from_to_date.to_date is not None:
            from_date = date_utils.date_to_localized_datetime(form.from_to_date.from_date, datetime.datetime.min.time())
            to_date = date_utils.date_to_localized_datetime(form.from_to_date.to_date, datetime.datetime.max.time())
            filters.append(
                sa.or_(
                    users_models.UserAccountUpdateRequest.dateLastStatusUpdate.between(from_date, to_date),
                    users_models.UserAccountUpdateRequest.dateLastUserMessage.between(from_date, to_date),
                )
            )

    if form.has_found_user.data and len(form.has_found_user.data) == 1:
        if form.has_found_user.data[0] == "true":
            filters.append(users_models.UserAccountUpdateRequest.userId.is_not(None))
        else:
            filters.append(users_models.UserAccountUpdateRequest.userId.is_(None))

    if form.status.data:
        filters.append(
            users_models.UserAccountUpdateRequest.status.in_(
                [dms_models.GraphQLApplicationStates[str(state)] for state in form.status.data]
            )
        )

    if form.update_type.data:
        filters.append(
            users_models.UserAccountUpdateRequest.updateTypes.contains(
                postgresql.array(type_ for type_ in form.update_type.data)
            )
        )

    if form.flags.data:
        filters.append(
            users_models.UserAccountUpdateRequest.flags.overlap(
                [users_models.UserAccountUpdateFlag[str(flag)] for flag in form.flags.data]
            )
        )

    if form.last_instructor.data:
        filters.append(users_models.UserAccountUpdateRequest.lastInstructorId.in_(form.last_instructor.data))

    if form.only_unassigned.data:
        filters.append(users_models.UserAccountUpdateRequest.lastInstructorId.is_(None))

    query = query.filter(*filters)
    return query


def _render_account_update_requests(account_update_requests_ids: list[int] | None = None) -> utils.BackofficeResponse:
    account_update_requests = []
    if account_update_requests_ids:
        query = _get_account_update_requests_query()
        account_update_requests = query.filter(
            users_models.UserAccountUpdateRequest.dsApplicationId.in_(account_update_requests_ids)
        ).all()
    return render_template(
        "accounts/update_requests_list_rows.html",
        update_requests=account_update_requests,
        is_instructor=(current_user.backoffice_profile.dsInstructorId is not None),
    )


@account_update_blueprint.route("", methods=["GET"])
def list_account_update_requests() -> utils.BackofficeResponse:
    form = account_forms.AccountUpdateRequestSearchForm(formdata=utils.get_query_params())
    if not form.validate():
        return render_template("accounts/update_requests_list.html", rows=[], form=form), 400

    query = _get_filtered_account_update_requests(form)
    query = query.order_by(getattr(users_models.UserAccountUpdateRequest.dateLastStatusUpdate, form.order.data)())

    paginated_rows = paginate(
        query=query,
        page=int(form.page.data),
        per_page=int(form.limit.data),
    )
    next_page = partial(url_for, ".list_account_update_requests", **form.raw_data)
    next_pages_urls = search_utils.pagination_links(next_page, int(form.page.data), paginated_rows.pages)
    form.page.data = 1  # Reset to first page when form is submitted ("Chercher" clicked)

    autocomplete.prefill_bo_users_choices(form.last_instructor)

    form_url = partial(url_for, ".list_account_update_requests", **form.raw_data)
    date_last_update_sort_url = form_url(order="desc" if form.order.data == "asc" else "asc")

    return render_template(
        "accounts/update_requests_list.html",
        rows=paginated_rows,
        form=form,
        next_pages_urls=next_pages_urls,
        is_instructor=(current_user.backoffice_profile.dsInstructorId is not None),
        date_last_update_sort_url=date_last_update_sort_url,
    )


@account_update_blueprint.route("<int:ds_application_id>/instruct", methods=["POST"])
def instruct(ds_application_id: int) -> utils.BackofficeResponse:
    if not current_user.backoffice_profile.dsInstructorId:
        raise Forbidden()

    update_request = (
        db.session.query(users_models.UserAccountUpdateRequest)
        .filter_by(dsApplicationId=ds_application_id)
        .populate_existing()
        .with_for_update(key_share=True)
        .one_or_none()
    )
    if not update_request:
        raise NotFound()

    try:
        users_ds.update_state(
            update_request,
            new_state=dms_models.GraphQLApplicationStates.on_going,
            instructor=current_user,
        )
    except dms_exceptions.DmsGraphQLApiError as err:
        flash(
            Markup("Le dossier <b>{ds_application_id}</b> ne peut pas passer en instruction : {message}").format(
                ds_application_id=ds_application_id,
                message="dossier non trouvé" if err.is_not_found else err.message,
            ),
            "warning",
        )
    except dms_exceptions.DmsGraphQLApiException as exc:
        flash(Markup("Une erreur s'est produite : {message}").format(message=str(exc)), "warning")
    return _render_account_update_requests([ds_application_id])


def _find_duplicate(update_request: users_models.UserAccountUpdateRequest) -> users_models.User | None:
    if not update_request.has_new_email or not update_request.newEmail:
        return None

    return (
        db.session.query(users_models.User)
        .filter_by(email=update_request.newEmail)
        .options(sa_orm.joinedload(users_models.User.deposits))
        .one_or_none()
    )


@account_update_blueprint.route("<int:ds_application_id>/accept", methods=["GET"])
def get_accept_form(ds_application_id: int) -> utils.BackofficeResponse:
    if not current_user.backoffice_profile.dsInstructorId:
        raise Forbidden()

    update_request = (
        db.session.query(users_models.UserAccountUpdateRequest)
        .filter_by(dsApplicationId=ds_application_id)
        .outerjoin(users_models.UserAccountUpdateRequest.user)
        .outerjoin(
            finance_models.Deposit,
            sa.and_(
                finance_models.Deposit.userId == users_models.User.id,
                finance_models.Deposit.expirationDate > date_utils.get_naive_utc_now(),
            ),
        )
        .options(
            sa_orm.contains_eager(users_models.UserAccountUpdateRequest.user).contains_eager(
                users_models.User.deposits
            ),
        )
        .one_or_none()
    )
    if not update_request:  # including when no userId is linked to the request
        raise NotFound()

    alert = None
    can_be_accepted = update_request.can_be_accepted
    if not can_be_accepted:
        alert = "La situation du dossier ne permet pas de l'accepter."

    duplicate_user = _find_duplicate(update_request)
    if duplicate_user:
        if duplicate_user.is_beneficiary or duplicate_user.deposits:
            can_be_accepted = False
            alert = "Un compte doublon avec la nouvelle adresse demandée a déjà reçu un crédit. Le dossier ne peut donc pas être accepté."
        elif duplicate_user.roles:
            alert = "Attention ! Le compte doublon qui sera suspendu est un compte pro ou admin."

    return render_template(
        "components/dynamic/modal_form.html",
        include_template="accounts/modal/accept_update_request.html",
        button_text="Appliquer les modifications et accepter" if can_be_accepted else None,
        target_id=f"#request-row-{ds_application_id}",
        title=f"Accepter le dossier Démarche Numérique n°{ds_application_id}",
        div_id=f"accept-{update_request.dsApplicationId}",
        ds_application_id=ds_application_id,
        update_request=update_request,
        duplicate_user=duplicate_user,
        can_be_accepted=can_be_accepted,
        alert=alert,
        form=account_forms.AccountUpdateRequestAcceptForm() if can_be_accepted else None,
        dst=url_for("backoffice_web.account_update.accept", ds_application_id=ds_application_id),
    )


@account_update_blueprint.route("<int:ds_application_id>/accept", methods=["POST"])
def accept(ds_application_id: int) -> utils.BackofficeResponse:
    if not current_user.backoffice_profile.dsInstructorId:
        raise Forbidden()

    form = account_forms.AccountUpdateRequestAcceptForm()
    if not form.validate():
        flash(utils.build_form_error_msg(form), "warning")
        return _render_account_update_requests()

    update_request: users_models.UserAccountUpdateRequest | None = (
        db.session.query(users_models.UserAccountUpdateRequest)
        .filter_by(dsApplicationId=ds_application_id)
        .populate_existing()
        .with_for_update(key_share=True)
        .one_or_none()
    )
    if not update_request:
        raise NotFound()

    user: users_models.User | None = (
        db.session.query(users_models.User)
        .filter_by(id=update_request.userId)
        .populate_existing()
        .with_for_update(key_share=True)
        .one_or_none()
    )
    if not user:
        raise NotFound()

    try:
        snapshot = users_api.update_user_info(
            user,
            author=current_user,
            first_name=(
                update_request.newFirstName
                if update_request.newFirstName and update_request.has_first_name_update
                else users_api.UNCHANGED
            ),
            last_name=(
                update_request.newLastName
                if update_request.newLastName and update_request.has_last_name_update
                else users_api.UNCHANGED
            ),
            phone_number=(
                update_request.newPhoneNumber if update_request.has_phone_number_update else users_api.UNCHANGED
            ),
            commit=False,
        )
        snapshot.add_action()
        db.session.flush()
    except sa.exc.IntegrityError as exc:
        mark_transaction_as_invalid()
        flash(Markup("Une erreur s'est produite : {message}").format(message=str(exc)), "warning")
        return _render_account_update_requests([ds_application_id])

    if update_request.has_new_email:
        duplicate_user = _find_duplicate(update_request)
        if duplicate_user:
            if duplicate_user.roles or duplicate_user.deposit:  # should be consistent but check both
                mark_transaction_as_invalid()
                flash(
                    Markup(
                        "Le dossier <b>{ds_application_id}</b> ne peut pas être accepté : l'email <b>{email}</b> "
                        "est déjà associé à un compte bénéficiaire ou ex-bénéficiaire, pro ou admin."
                    ).format(ds_application_id=ds_application_id, email=update_request.newEmail),
                    "warning",
                )
                return _render_account_update_requests([ds_application_id])

            users_api.suspend_account(
                duplicate_user,
                reason=users_constants.SuspensionReason.DUPLICATE_REPORTED_BY_USER,
                actor=current_user,
                action_extra_data={
                    "ds_procedure_id": int(settings.DS_USER_ACCOUNT_UPDATE_PROCEDURE_ID),
                    "ds_dossier_id": ds_application_id,
                },
                is_backoffice_action=True,
            )
            email_update.clear_email_by_admin(duplicate_user)

        assert update_request.newEmail  # helps mypy
        # EmailExistsError should not happen because of duplicate check above
        email_update.full_email_update_by_admin(user, update_request.newEmail)
        db.session.flush()

    external_attributes_api.update_external_user(user)
    send_beneficiary_personal_data_updated(
        user,
        is_first_name_updated=update_request.has_first_name_update,
        is_last_name_updated=update_request.has_last_name_update,
        is_email_updated=update_request.has_new_email,
        is_phone_number_updated=update_request.has_phone_number_update,
    )

    try:
        users_ds.update_state(
            update_request,
            new_state=dms_models.GraphQLApplicationStates.accepted,
            instructor=current_user,
            motivation=form.motivation.data,
        )
    except dms_exceptions.DmsGraphQLApiError as err:
        mark_transaction_as_invalid()
        flash(
            Markup("Le dossier <b>{ds_application_id}</b> ne peut pas être accepté : {message}").format(
                ds_application_id=ds_application_id,
                message="dossier non trouvé" if err.is_not_found else err.message,
            ),
            "warning",
        )
    except dms_exceptions.DmsGraphQLApiException as exc:
        mark_transaction_as_invalid()
        flash(Markup("Une erreur s'est produite : {message}").format(message=str(exc)), "warning")
    else:
        history_api.add_action(
            history_models.ActionType.USER_ACCOUNT_UPDATE_INSTRUCTED,
            author=current_user,
            user=user,
            comment=form.motivation.data,
            ds_procedure_id=int(settings.DS_USER_ACCOUNT_UPDATE_PROCEDURE_ID),
            ds_dossier_id=ds_application_id,
            ds_status=update_request.status,
        )
        db.session.flush()

    return _render_account_update_requests([ds_application_id])


@account_update_blueprint.route("<int:ds_application_id>/ask-for-correction", methods=["GET"])
def get_ask_for_correction_form(ds_application_id: int) -> utils.BackofficeResponse:
    if not current_user.backoffice_profile.dsInstructorId:
        raise Forbidden()

    update_request = (
        db.session.query(users_models.UserAccountUpdateRequest)
        .filter_by(dsApplicationId=ds_application_id)
        .one_or_none()
    )
    if not update_request:
        raise NotFound()

    correction_reason = account_forms.AccountUpdateRequestCorrectionForm(request.args).correction_reason.data

    return render_template(
        "components/dynamic/modal_form.html",
        target_id=f"#request-row-{ds_application_id}",
        form=empty_forms.EmptyForm(),
        dst=url_for(
            "backoffice_web.account_update.ask_for_correction",
            ds_application_id=ds_application_id,
            correction_reason=correction_reason,
        ),
        div_id=f"ask-for-correction-{correction_reason}-{ds_application_id}",
        title="Demander une correction",
        information=Markup("Ce message sera envoyé au jeune : <br><br>")
        + filters.nl2br(users_ds.CORRECTION_MESSAGE[correction_reason]),
        button_text="Faire une demande de correction",
    )


@account_update_blueprint.route("<int:ds_application_id>/ask-for-correction", methods=["POST"])
def ask_for_correction(ds_application_id: int) -> utils.BackofficeResponse:
    if not current_user.backoffice_profile.dsInstructorId:
        raise Forbidden()

    update_request: users_models.UserAccountUpdateRequest | None = (
        db.session.query(users_models.UserAccountUpdateRequest)
        .filter_by(dsApplicationId=ds_application_id)
        .populate_existing()
        .with_for_update(key_share=True)
        .one_or_none()
    )
    if not update_request:
        raise NotFound()

    form = account_forms.AccountUpdateRequestCorrectionForm(request.args)
    if not form.validate():
        flash(utils.build_form_error_msg(form), "warning")
        return _render_account_update_requests([ds_application_id])

    correction_reason = form.correction_reason.data

    send_beneficiary_update_request_ask_for_correction(update_request, correction_reason)
    try:
        users_ds.send_user_message_with_correction(update_request, current_user, correction_reason)
    except dms_exceptions.DmsGraphQLApiError as err:
        mark_transaction_as_invalid()
        flash(
            Markup(
                "Le dossier <b>{ds_application_id}</b> ne peut pas recevoir de demande de correction : {message}"
            ).format(
                ds_application_id=ds_application_id,
                message="dossier non trouvé" if err.is_not_found else err.message,
            ),
            "warning",
        )
    except sa.exc.IntegrityError as exc:
        mark_transaction_as_invalid()
        flash(Markup("Une erreur s'est produite : {message}").format(message=str(exc)), "warning")
        return _render_account_update_requests([ds_application_id])

    return _render_account_update_requests([ds_application_id])


@account_update_blueprint.route("<int:ds_application_id>/identity-theft", methods=["GET"])
def get_identity_theft_form(ds_application_id: int) -> utils.BackofficeResponse:
    if not current_user.backoffice_profile.dsInstructorId:
        raise Forbidden()

    update_request = (
        db.session.query(users_models.UserAccountUpdateRequest)
        .filter_by(dsApplicationId=ds_application_id)
        .one_or_none()
    )
    if not update_request:
        raise NotFound()

    form = empty_forms.EmptyForm()

    return render_template(
        "components/dynamic/modal_form.html",
        target_id=f"#request-row-{ds_application_id}",
        form=form,
        dst=url_for(".identity_theft", ds_application_id=ds_application_id),
        div_id=f"identity-theft-{ds_application_id}",
        title="Usurpation d'identité",
        information="Ce message sera envoyé au jeune: <br>" + users_ds.IDENTITY_THEFT_MESSAGE,
        button_text="Rejeter pour usurpation d'identité",
    )


@account_update_blueprint.route("<int:ds_application_id>/identity-theft", methods=["POST"])
def identity_theft(ds_application_id: int) -> utils.BackofficeResponse:
    if not current_user.backoffice_profile.dsInstructorId:
        raise Forbidden()

    update_request: users_models.UserAccountUpdateRequest | None = (
        db.session.query(users_models.UserAccountUpdateRequest)
        .filter_by(dsApplicationId=ds_application_id)
        .populate_existing()
        .with_for_update(key_share=True)
        .one_or_none()
    )
    if not update_request:
        raise NotFound()

    send_beneficiary_update_request_identity_theft(update_request)

    try:
        users_ds.update_state(
            update_request,
            new_state=dms_models.GraphQLApplicationStates.refused,
            instructor=current_user,
            motivation=users_ds.IDENTITY_THEFT_MESSAGE,
        )
    except dms_exceptions.DmsGraphQLApiError as err:
        mark_transaction_as_invalid()
        flash(
            Markup("Le dossier <b>{ds_application_id}</b> ne peut pas être rejeté : {message}").format(
                ds_application_id=ds_application_id,
                message="dossier non trouvé" if err.is_not_found else err.message,
            ),
            "warning",
        )
    except sa.exc.IntegrityError as exc:
        mark_transaction_as_invalid()
        flash(Markup("Une erreur s'est produite : {message}").format(message=str(exc)), "warning")
        return _render_account_update_requests([ds_application_id])

    return _render_account_update_requests([ds_application_id])


@account_update_blueprint.route("<int:ds_application_id>/select-user", methods=["GET"])
def get_select_user_form(ds_application_id: int) -> utils.BackofficeResponse:
    update_request = (
        db.session.query(users_models.UserAccountUpdateRequest)
        .filter_by(dsApplicationId=ds_application_id)
        .one_or_none()
    )
    if not update_request:
        raise NotFound()

    title = "Remplacer le compte jeune" if update_request.userId else "Renseigner le compte jeune"

    if update_request.is_closed:
        # May have been updated by another instructor between display and click on action
        return render_template(
            "components/dynamic/modal_form.html",
            div_id=f"select-user-{ds_application_id}",
            title=title,
            alert=Markup("Le dossier n°{ds_application_id} est déjà instruit.").format(
                ds_application_id=ds_application_id
            ),
        )

    form = account_forms.AccountUpdateRequestSelectUserForm(
        user=[update_request.userId] if update_request.userId else None,  # type: ignore[arg-type]
    )

    return render_template(
        "components/dynamic/modal_form.html",
        target_id=f"#request-row-{ds_application_id}",
        form=form,
        dst=url_for(".select_user", ds_application_id=ds_application_id),
        div_id=f"select-user-{ds_application_id}",
        title=title,
        information=Markup(
            "Sélectionnez un compte jeune à associer au dossier Démarche Numérique n°<strong>{ds_application_id}</strong>."
        ).format(ds_application_id=ds_application_id),
        button_text="Continuer",
    )


@account_update_blueprint.route("<int:ds_application_id>/select-user", methods=["POST"])
def select_user(ds_application_id: int) -> utils.BackofficeResponse:
    update_request: users_models.UserAccountUpdateRequest | None = (
        db.session.query(users_models.UserAccountUpdateRequest)
        .filter_by(dsApplicationId=ds_application_id)
        .populate_existing()
        .with_for_update(key_share=True)
        .one_or_none()
    )
    if not update_request:
        raise NotFound()

    if update_request.is_closed:
        flash(
            Markup("Le dossier n°{ds_application_id} est déjà instruit.").format(ds_application_id=ds_application_id),
            "warning",
        )
        return _render_account_update_requests([ds_application_id])

    form = account_forms.AccountUpdateRequestSelectUserForm()
    if not form.validate():
        flash(utils.build_form_error_msg(form), "warning")
        return _render_account_update_requests([ds_application_id])

    update_request.set_user_id(form.user.data[0])
    db.session.add(update_request)
    db.session.flush()

    return _render_account_update_requests([ds_application_id])
