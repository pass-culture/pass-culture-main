import datetime
from functools import partial

from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from flask_login import current_user
from markupsafe import Markup
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from werkzeug.exceptions import Forbidden
from werkzeug.exceptions import NotFound

from pcapi import settings
from pcapi.connectors.dms import exceptions as dms_exceptions
from pcapi.connectors.dms import models as dms_models
from pcapi.core.external.attributes import api as external_attributes_api
from pcapi.core.history import api as history_api
from pcapi.core.history import models as history_models
from pcapi.core.mails.transactional.users.personal_data_updated import send_beneficiary_personal_data_updated
from pcapi.core.permissions import models as perm_models
from pcapi.core.subscription.phone_validation import exceptions as phone_validation_exceptions
from pcapi.core.users import api as users_api
from pcapi.core.users import constants as users_constants
from pcapi.core.users import ds as users_ds
from pcapi.core.users import models as users_models
from pcapi.core.users.email import update as email_update
from pcapi.models import db
from pcapi.models.pc_object import BaseQuery
from pcapi.repository import atomic
from pcapi.repository import mark_transaction_as_invalid
from pcapi.repository import on_commit
from pcapi.routes.backoffice import autocomplete
from pcapi.routes.backoffice import search_utils
from pcapi.routes.backoffice import utils
from pcapi.utils import date as date_utils
from pcapi.utils import email as email_utils
from pcapi.utils import phone_number as phone_number_utils
from pcapi.utils.clean_accents import clean_accents

from . import forms as account_forms


account_update_blueprint = utils.child_backoffice_blueprint(
    "account_update",
    __name__,
    url_prefix="/account-update-requests",
    permission=perm_models.Permissions.MANAGE_ACCOUNT_UPDATE_REQUEST,
)


def _get_filtered_account_update_requests(form: account_forms.AccountUpdateRequestSearchForm) -> BaseQuery:

    aliased_instructor = sa.orm.aliased(users_models.User)

    query = (
        users_models.UserAccountUpdateRequest.query.outerjoin(
            users_models.User, users_models.UserAccountUpdateRequest.userId == users_models.User.id
        )
        .outerjoin(aliased_instructor, users_models.UserAccountUpdateRequest.lastInstructorId == aliased_instructor.id)
        .options(
            sa.orm.contains_eager(users_models.UserAccountUpdateRequest.user).load_only(
                users_models.User.id,
                users_models.User.firstName,
                users_models.User.lastName,
                users_models.User.email,
                users_models.User.phoneNumber,
                users_models.User.dateOfBirth,
                users_models.User.validatedBirthDate,
                users_models.User.civility,
                users_models.User.roles,
            ),
            sa.orm.contains_eager(
                users_models.UserAccountUpdateRequest.lastInstructor.of_type(aliased_instructor)
            ).load_only(
                aliased_instructor.id,
                aliased_instructor.email,
                aliased_instructor.firstName,
                aliased_instructor.lastName,
            ),
        )
    )

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
                sa.or_(  # type: ignore[type-var]
                    users_models.User.phoneNumber == term_as_phone_number,
                    users_models.UserAccountUpdateRequest.newPhoneNumber == term_as_phone_number,
                )
            )

        # numeric
        if search_query.isnumeric():
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
        filters.append(aliased_instructor.id.in_(form.last_instructor.data))

    query = query.filter(*filters)
    return query


@account_update_blueprint.route("", methods=["GET"])
@atomic()
def list_account_update_requests() -> utils.BackofficeResponse:
    form = account_forms.AccountUpdateRequestSearchForm(formdata=utils.get_query_params())
    if not form.validate():
        return render_template("accounts/update_requests_list.html", rows=[], form=form), 400

    query = _get_filtered_account_update_requests(form)
    query = query.order_by(users_models.UserAccountUpdateRequest.dateLastStatusUpdate.desc())

    paginated_rows = query.paginate(page=int(form.page.data), per_page=int(form.per_page.data))
    next_page = partial(url_for, ".list_account_update_requests", **form.raw_data)
    next_pages_urls = search_utils.pagination_links(next_page, int(form.page.data), paginated_rows.pages)
    form.page.data = 1  # Reset to first page when form is submitted ("Chercher" clicked)

    autocomplete.prefill_bo_users_choices(form.last_instructor)

    return render_template(
        "accounts/update_requests_list.html",
        rows=paginated_rows,
        form=form,
        next_pages_urls=next_pages_urls,
        is_instructor=(current_user.backoffice_profile.dsInstructorId is not None),
    )


def _refresh_list() -> utils.BackofficeResponse:
    return redirect(request.referrer or url_for(".list_account_update_requests"), code=303)


@account_update_blueprint.route("<int:ds_application_id>/instruct", methods=["POST"])
@atomic()
def instruct(ds_application_id: int) -> utils.BackofficeResponse:
    if not current_user.backoffice_profile.dsInstructorId:
        raise Forbidden()

    update_request = (
        users_models.UserAccountUpdateRequest.query.filter_by(dsApplicationId=ds_application_id)
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
                message="dossier non trouvé" if err.code == "not_found" else err.message,
            ),
            "warning",
        )
    except dms_exceptions.DmsGraphQLApiException as exc:
        flash(Markup("Une erreur s'est produite : {message}").format(message=str(exc)), "warning")

    return _refresh_list()


def _find_duplicate(update_request: users_models.UserAccountUpdateRequest) -> users_models.User | None:
    if not update_request.has_email_update or not update_request.newEmail:
        return None

    return (
        users_models.User.query.filter_by(email=update_request.newEmail)
        .options(sa.orm.joinedload(users_models.User.deposits))
        .one_or_none()
    )


@account_update_blueprint.route("<int:ds_application_id>/accept", methods=["GET"])
@atomic()
def get_accept_form(ds_application_id: int) -> utils.BackofficeResponse:
    if not current_user.backoffice_profile.dsInstructorId:
        raise Forbidden()

    update_request = (
        users_models.UserAccountUpdateRequest.query.filter_by(dsApplicationId=ds_application_id)
        .options(sa.orm.joinedload(users_models.UserAccountUpdateRequest.user))
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
        "accounts/modal/accept_update_request.html",
        ds_application_id=ds_application_id,
        update_request=update_request,
        duplicate_user=duplicate_user,
        can_be_accepted=can_be_accepted,
        alert=alert,
        form=account_forms.AccountUpdateRequestAcceptForm(),
        dst=url_for(".accept", ds_application_id=ds_application_id),
    )


@account_update_blueprint.route("<int:ds_application_id>/accept", methods=["POST"])
@atomic()
def accept(ds_application_id: int) -> utils.BackofficeResponse:
    if not current_user.backoffice_profile.dsInstructorId:
        raise Forbidden()

    form = account_forms.AccountUpdateRequestAcceptForm()
    if not form.validate():
        flash(utils.build_form_error_msg(form), "warning")
        return _refresh_list()

    update_request: users_models.UserAccountUpdateRequest = (
        users_models.UserAccountUpdateRequest.query.filter_by(dsApplicationId=ds_application_id)
        .populate_existing()
        .with_for_update(key_share=True)
        .one_or_none()
    )
    if not update_request:
        raise NotFound()

    user: users_models.User = (
        users_models.User.query.filter_by(id=update_request.userId)
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
            first_name=(update_request.newFirstName if update_request.has_first_name_update else users_api.UNCHANGED),
            last_name=(update_request.newLastName if update_request.has_last_name_update else users_api.UNCHANGED),
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
        return _refresh_list()

    if update_request.has_email_update:
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
                return _refresh_list()

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

        # EmailExistsError should not happen because of duplicate check above
        email_update.full_email_update_by_admin(user, update_request.newEmail)
        db.session.flush()

    on_commit(partial(external_attributes_api.update_external_user, user))
    on_commit(
        partial(
            send_beneficiary_personal_data_updated,
            user,
            is_first_name_updated=update_request.has_first_name_update,
            is_last_name_updated=update_request.has_last_name_update,
            is_email_updated=update_request.has_email_update,
            is_phone_number_updated=update_request.has_phone_number_update,
        ),
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
                message="dossier non trouvé" if err.code == "not_found" else err.message,
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

    return _refresh_list()
