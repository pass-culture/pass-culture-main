import datetime
import enum
import re
import typing
from functools import partial
from operator import attrgetter
from types import NotImplementedType

import sqlalchemy as sa
import sqlalchemy.orm as sa_orm
from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from flask_login import current_user
from markupsafe import Markup
from werkzeug.exceptions import BadRequest
from werkzeug.exceptions import NotFound

from pcapi import settings
from pcapi.core.bookings import models as bookings_models
from pcapi.core.chronicles import models as chronicles_models
from pcapi.core.external.attributes import api as external_attributes_api
from pcapi.core.finance import deposit_api
from pcapi.core.finance import exceptions as finance_exceptions
from pcapi.core.finance import models as finance_models
from pcapi.core.fraud import exceptions as fraud_exceptions
from pcapi.core.geography import models as geography_models
from pcapi.core.history import api as history_api
from pcapi.core.history import models as history_models
from pcapi.core.mails.transactional.users.personal_data_updated import send_beneficiary_personal_data_updated
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offers import models as offers_models
from pcapi.core.operations import models as operations_models
from pcapi.core.permissions import models as perm_models
from pcapi.core.subscription import api as subscription_api
from pcapi.core.subscription import exceptions as subscription_exceptions
from pcapi.core.subscription import fraud_check_api as fraud_api
from pcapi.core.subscription import models as subscription_models
from pcapi.core.subscription import schemas as subscription_schemas
from pcapi.core.subscription.bonus import constants as bonus_constants
from pcapi.core.subscription.bonus import fraud_check_api as bonus_fraud_api
from pcapi.core.subscription.bonus import schemas as bonus_schemas
from pcapi.core.subscription.bonus import tasks as bonus_tasks
from pcapi.core.subscription.phone_validation import api as phone_validation_api
from pcapi.core.subscription.phone_validation import exceptions as phone_validation_exceptions
from pcapi.core.users import api as users_api
from pcapi.core.users import constants as users_constants
from pcapi.core.users import eligibility_api
from pcapi.core.users import exceptions as users_exceptions
from pcapi.core.users import gdpr_api
from pcapi.core.users import models as users_models
from pcapi.core.users import utils as users_utils
from pcapi.core.users.email import update as email_update
from pcapi.core.users.password_utils import random_password
from pcapi.models import db
from pcapi.models.beneficiary_import import BeneficiaryImport
from pcapi.models.beneficiary_import_status import BeneficiaryImportStatus
from pcapi.models.feature import DisabledFeatureError
from pcapi.routes.backoffice import autocomplete
from pcapi.routes.backoffice import search_utils
from pcapi.routes.backoffice import utils
from pcapi.routes.backoffice.bookings import helpers as booking_helpers
from pcapi.routes.backoffice.forms import empty as empty_forms
from pcapi.routes.backoffice.users import forms as user_forms
from pcapi.utils import date as date_utils
from pcapi.utils import email as email_utils
from pcapi.utils.transaction_manager import atomic
from pcapi.utils.transaction_manager import mark_transaction_as_invalid
from pcapi.utils.transaction_manager import on_commit

from . import forms as account_forms
from . import serialization


OptionableType = typing.TypeVar("OptionableType", bound="sa.orm.Query | sa.orm.strategy_options._AbstractLoad")

public_accounts_blueprint = utils.child_backoffice_blueprint(
    "public_accounts",
    __name__,
    url_prefix="/public-accounts",
    permission=perm_models.Permissions.READ_PUBLIC_ACCOUNT,
)


def _load_suspension_info(query: sa_orm.Query) -> sa_orm.Query:
    # Partial joined load with ActionHistory avoids N+1 query to show suspension reason, but the number of fetched rows
    # would be greater than the number of results when a single user has several suspension actions.
    # So these expressions use a subquery so that result count is accurate, and the redirection well forced when a
    # single card would be displayed.
    return query.options(
        sa_orm.with_expression(
            users_models.User.suspension_reason_expression,
            users_models.User.suspension_reason.expression,
        ),
        sa_orm.with_expression(
            users_models.User.suspension_date_expression,
            users_models.User.suspension_date.expression,
        ),
    )


def _load_current_deposit_data(query: sa_orm.Query, join_needed: bool = True) -> sa_orm.Query:
    # partial joined load with Deposit and Recredit to avoid N+1, show the version of the current
    # deposit and not mess with the pagination as a beneficiary cannot have multiple deposits active
    # at the same time
    if join_needed:
        query = query.outerjoin(
            finance_models.Deposit,
            sa.and_(
                users_models.User.id == finance_models.Deposit.userId,
                finance_models.Deposit.expirationDate > date_utils.get_naive_utc_now(),
            ),
        )
    return query.options(sa_orm.contains_eager(users_models.User.deposits))


@public_accounts_blueprint.route("<int:user_id>/tags", methods=["POST"])
@utils.permission_required(perm_models.Permissions.MANAGE_ACCOUNT_TAGS)
def tag_public_account(user_id: int) -> utils.BackofficeResponse:
    user = (
        db.session.query(users_models.User)
        .filter(users_models.User.id == user_id)
        .options(
            sa_orm.load_only(users_models.User.id),
            sa_orm.joinedload(users_models.User.tags).load_only(users_models.UserTag.id, users_models.UserTag.label),
        )
        .one_or_none()
    )
    if not user:
        raise NotFound()

    form = account_forms.TagAccountForm()
    if not form.validate():
        flash(utils.build_form_error_msg(form), "warning")
        return redirect(url_for(".get_public_account", user_id=user_id), code=303)

    old_tags = {str(tag) for tag in user.tags}
    new_tags = {str(tag) for tag in form.tags.data}
    removed_tags = old_tags - new_tags
    added_tags = new_tags - old_tags

    user.tags = form.tags.data

    if added_tags or removed_tags:
        history_api.add_action(
            history_models.ActionType.INFO_MODIFIED,
            author=current_user,
            user=user,
            modified_info={"tags": {"old_info": sorted(removed_tags) or None, "new_info": sorted(added_tags) or None}},
        )

    db.session.add(user)
    db.session.flush()

    flash("Tags mis à jour avec succès", "success")

    return redirect(url_for(".get_public_account", user_id=user_id, active_tab="history"), code=303)


@public_accounts_blueprint.route("<int:user_id>/anonymize", methods=["POST"])
@utils.permission_required(perm_models.Permissions.ANONYMIZE_PUBLIC_ACCOUNT)
def anonymize_public_account(user_id: int) -> utils.BackofficeResponse:
    user = (
        db.session.query(users_models.User)
        .filter_by(id=user_id)
        .options(
            sa_orm.joinedload(users_models.User.deposits),
            sa_orm.joinedload(users_models.User.gdprUserDataExtracts),
        )
        .one_or_none()
    )

    if not user:
        raise NotFound()

    form = empty_forms.EmptyForm()
    if not form.validate():
        flash(utils.build_form_error_msg(form), "warning")
        return redirect(url_for("backoffice_web.public_accounts.get_public_account", user_id=user_id), code=303)

    if gdpr_api.has_unprocessed_extract(user):
        flash("Une extraction de données est en cours pour cet utilisateur.", "warning")
        return redirect(url_for(".get_public_account", user_id=user_id))

    if gdpr_api.is_beneficiary_anonymizable(user):
        _anonymize_user(user, current_user)
    elif gdpr_api.is_only_beneficiary(user):
        _pre_anonymize_user(user, current_user)
    else:
        raise BadRequest()

    return redirect(url_for(".get_public_account", user_id=user_id))


def _anonymize_user(user: users_models.User, author: users_models.User) -> None:
    user_anonymized = gdpr_api.anonymize_user(user, author=current_user)
    if user_anonymized:
        db.session.flush()
        flash("Les informations de l'utilisateur ont été anonymisées", "success")
    else:
        mark_transaction_as_invalid()
        flash("Une erreur est survenue lors de l'anonymisation de l'utilisateur", "warning")


def _pre_anonymize_user(user: users_models.User, author: users_models.User) -> None:
    if gdpr_api.is_suspended_for_less_than_five_years(user):
        db.session.add(users_models.GdprUserAnonymization(user=user))
        db.session.flush()
        flash(
            "L'utilisateur sera anonymisé quand il aura plus de 21 ans et 5 ans après sa suspension pour fraude",
            "success",
        )
    else:
        try:
            gdpr_api.pre_anonymize_user(user, author, is_backoffice_action=True)
        except users_exceptions.UserAlreadyHasPendingAnonymization:
            mark_transaction_as_invalid()
            flash("L'utilisateur est déjà en attente pour être anonymisé le jour de ses 21 ans", "warning")
        else:
            db.session.flush()
            flash("L'utilisateur a été suspendu et sera anonymisé le jour de ses 21 ans", "success")


@public_accounts_blueprint.route("/search", methods=["GET"])
def search_public_accounts() -> utils.BackofficeResponse:
    """
    Renders two search pages: first the one with the search form, then
    the one of the results.
    """
    if not request.args:
        return render_search_template()

    form = account_forms.AccountSearchForm(request.args)
    form.tag.choices = [(tag.id, str(tag)) for tag in get_user_tags()]
    if not form.validate():
        flash(utils.build_form_error_msg(form), "warning")
        return render_search_template(form), 400

    users_query = users_api.search_public_account(form.q.data)
    users_query = search_utils.apply_filter_on_beneficiary_status(users_query, form.filter.data)
    users_query = users_api.apply_filter_on_beneficiary_tag(users_query, form.tag.data)
    users_query = _load_suspension_info(users_query)
    users_query = _load_current_deposit_data(users_query, join_needed=False)
    paginated_rows = search_utils.paginate(
        query=users_query,
        page=form.page.data,
        per_page=form.per_page.data,
    )

    # Do NOT call users.count() after search_public_account, this would make one more request on all users every time
    # (so it would select count twice: in users.count() and in users.paginate)
    if (
        paginated_rows.total == 0
        and form.q.data
        and email_utils.is_valid_email(email_utils.sanitize_email(form.q.data))
    ):
        users_query = users_api.search_public_account_in_history_email(form.q.data)
        users_query = users_api.apply_filter_on_beneficiary_tag(users_query, form.tag.data)
        users_query = _load_suspension_info(users_query)
        users_query = _load_current_deposit_data(users_query)
        paginated_rows = search_utils.paginate(
            users_query,
            page=form.page.data,
            per_page=form.per_page.data,
        )

    if paginated_rows.total == 1:
        return redirect(
            url_for(
                ".get_public_account",
                user_id=paginated_rows.items[0].id,
                q=form.q.data,
                filter=form.filter.data,
                tag=form.tag.data,
                search_rank=1,
                total_items=1,
            ),
            code=303,
        )

    next_page = partial(url_for, ".search_public_accounts", **form.raw_data)
    next_pages_urls = search_utils.pagination_links(next_page, form.page.data, paginated_rows.pages)

    form.page.data = 1  # Reset to first page when form is submitted ("Chercher" clicked)

    return render_template(
        "accounts/search_result.html",
        search_form=form,
        search_dst=url_for(".search_public_accounts"),
        next_pages_urls=next_pages_urls,
        get_link_to_detail=get_public_account_link,
        rows=paginated_rows,
    )


def render_search_template(form: account_forms.AccountSearchForm | None = None) -> str:
    if not form:
        form = account_forms.AccountSearchForm()
        form.tag.choices = [(tag.id, str(tag)) for tag in get_user_tags()]

    return render_template(
        "accounts/search.html",
        title="Recherche grand public",
        dst=url_for(".search_public_accounts"),
        form=form,
    )


def _convert_fraud_review_to_fraud_action_dict(fraud_review: subscription_models.BeneficiaryFraudReview) -> dict:
    return {
        "creationDate": fraud_review.dateReviewed,
        "type": "Revue manuelle",
        "applicableEligibilities": (
            [fraud_review.eligibilityType.value] if fraud_review.eligibilityType is not None else []
        ),
        "status": subscription_models.FraudReviewStatus(fraud_review.review).value,
        "reason": fraud_review.reason,
    }


def _convert_check_item_to_fraud_action_dict(id_check_item: serialization.IdCheckItemModel) -> dict:
    return {
        "creationDate": id_check_item.dateCreated,
        "techId": id_check_item.thirdPartyId,
        "type": id_check_item.type,
        "applicableEligibilities": id_check_item.applicable_eligibilities,
        "status": id_check_item.status,
        "reason": id_check_item.reason,
        "errorCode": id_check_item.reasonCodes,
        "technicalDetails": id_check_item.technicalDetails,
    }


def get_user_tags() -> list[users_models.UserTag]:
    return db.session.query(users_models.UserTag).order_by(users_models.UserTag.label, users_models.UserTag.name).all()


def _apply_bookings_joined_loads(query: OptionableType) -> OptionableType:
    result = query.options(
        sa_orm.joinedload(bookings_models.Booking.stock, innerjoin=True)
        .joinedload(offers_models.Stock.offer, innerjoin=True)
        .joinedload(offers_models.Offer.offererAddress)
        .load_only()
        .joinedload(offerers_models.OffererAddress.address)
        .load_only(geography_models.Address.timezone),
        sa_orm.joinedload(bookings_models.Booking.incidents).joinedload(finance_models.BookingFinanceIncident.incident),
        sa_orm.joinedload(bookings_models.Booking.offerer, innerjoin=True).load_only(offerers_models.Offerer.name),
        sa_orm.joinedload(bookings_models.Booking.venue, innerjoin=True)
        .load_only(offerers_models.Venue.bookingEmail)
        .joinedload(offerers_models.Venue.contact)
        .load_only(offerers_models.VenueContact.email),
        sa_orm.joinedload(bookings_models.Booking.fraudulentBookingTag),
    )
    return typing.cast(OptionableType, result)


def render_public_account_details(
    user_id: int,
    edit_account_form: account_forms.EditAccountForm | None = None,
) -> str:
    # Using subqueryload to avoid huge cartesian product which would cause timeout when fetching too many rows.
    # 9 SQL queries require less resources than a single query with multiple 1-n joinedloads.
    # Note that extra queries are made in methods called by get_eligibility_history()
    user = (
        db.session.query(users_models.User)
        .filter_by(id=user_id)
        .options(
            sa_orm.joinedload(users_models.User.deposits).joinedload(finance_models.Deposit.recredits),
            _apply_bookings_joined_loads(sa_orm.subqueryload(users_models.User.userBookings)),
            sa_orm.subqueryload(users_models.User.beneficiaryFraudChecks),
            sa_orm.subqueryload(users_models.User.beneficiaryFraudReviews),
            sa_orm.subqueryload(users_models.User.beneficiaryImports)
            .joinedload(BeneficiaryImport.statuses)
            .joinedload(BeneficiaryImportStatus.author)
            .load_only(  # User.full_name
                users_models.User.firstName, users_models.User.lastName, users_models.User.email
            ),
            sa_orm.subqueryload(users_models.User.action_history)
            .joinedload(history_models.ActionHistory.authorUser)
            .load_only(  # User.full_name
                users_models.User.firstName, users_models.User.lastName, users_models.User.email
            ),
            sa_orm.subqueryload(users_models.User.email_history),
            sa_orm.subqueryload(users_models.User.gdprUserDataExtracts),
            sa_orm.subqueryload(users_models.User.tags),
        )
        .one_or_none()
    )

    if not user:
        raise NotFound()

    has_changed_email = any(
        email_event.eventType
        not in (
            users_models.EmailHistoryEventTypeEnum.UPDATE_REQUEST,  # step 1/4
            users_models.EmailHistoryEventTypeEnum.CONFIRMATION,  # step 2/4
            users_models.EmailHistoryEventTypeEnum.NEW_EMAIL_SELECTION,  # step 3/4
            users_models.EmailHistoryEventTypeEnum.CANCELLATION,
        )
        for email_event in user.email_history
    )

    domains_credit = (
        users_api.get_domains_credit(user, user_bookings=user.userBookings) if user.is_beneficiary else None
    )
    history = get_public_account_history(user, bo_user=current_user)
    duplicate_user_id = None
    eligibility_history = get_eligibility_history(user)
    user_current_eligibility = eligibility_api.get_eligibility_at_date(user.birth_date, date_utils.get_naive_utc_now())

    if user_current_eligibility is not None and user_current_eligibility.value in eligibility_history:
        subscription_items = [
            item
            for item in eligibility_history[user_current_eligibility.value].subscriptionItems
            if item.type == subscription_schemas.SubscriptionStep.IDENTITY_CHECK.value
            and item.status != subscription_schemas.SubscriptionItemStatus.OK.value
        ]

        if eligibility_history[user_current_eligibility.value].idCheckHistory and len(subscription_items) > 0:
            duplicate_user_id = _get_duplicate_fraud_history(eligibility_history)

    latest_fraud_check = _get_latest_fraud_check(
        eligibility_history, [subscription_models.FraudCheckType.UBBLE, subscription_models.FraudCheckType.DMS]
    )

    kwargs: dict[str, typing.Any] = {}

    if utils.has_current_user_permission(perm_models.Permissions.MANAGE_PUBLIC_ACCOUNT):
        if not edit_account_form:
            edit_account_form = account_forms.EditAccountForm(
                last_name=user.lastName,
                first_name=user.firstName,
                email=user.email,
                birth_date=user.birth_date,
                phone_number=user.phoneNumber,
                id_piece_number=user.idPieceNumber,
                postal_address_autocomplete=(
                    f"{user.address}, {user.postalCode} {user.city}"
                    if user.address is not None and user.city is not None and user.postalCode is not None
                    else None
                ),
                street=user.address,
                postal_code=user.postalCode,
                city=user.city,
                marketing_email_subscription=user.get_notification_subscriptions().marketing_email,
            )
        extract_user_form = None
        if utils.has_current_user_permission(perm_models.Permissions.EXTRACT_PUBLIC_ACCOUNT):
            if user.is_beneficiary or user.roles == []:
                extract_user_form = empty_forms.EmptyForm()
        if utils.has_current_user_permission(perm_models.Permissions.MANAGE_PUBLIC_ACCOUNT):
            kwargs.update(
                {
                    "password_reset_dst": url_for(".send_public_account_reset_password_email", user_id=user.id),
                    "password_reset_form": empty_forms.EmptyForm(),
                    "password_invalidation_dst": url_for(".invalidate_public_account_password", user_id=user.id),
                    "password_invalidation_form": empty_forms.EmptyForm(),
                }
            )

        manual_review_form = None
        if utils.has_current_user_permission(perm_models.Permissions.BENEFICIARY_MANUAL_REVIEW):
            manual_review_form = account_forms.ManualReviewForm()

        can_request_bonus_credit = utils.has_current_user_permission(
            perm_models.Permissions.REQUEST_BENEFICIARY_BONUS_CREDIT
        ) and users_api.get_user_is_eligible_for_bonification(user, is_from_backoffice=True)

        kwargs.update(
            {
                "edit_account_form": edit_account_form,
                "edit_account_dst": url_for(".update_public_account", user_id=user.id),
                "manual_review_form": manual_review_form,
                "manual_review_dst": url_for(".review_public_account", user_id=user.id),
                "can_request_bonus_credit": can_request_bonus_credit,
                "send_validation_code_form": empty_forms.EmptyForm(),
                "manual_phone_validation_form": empty_forms.EmptyForm(),
                "extract_user_form": extract_user_form,
            }
        )

        if not user.isEmailValidated:
            kwargs["resend_email_validation_form"] = empty_forms.EmptyForm()

    if (
        utils.has_current_user_permission(perm_models.Permissions.ANONYMIZE_PUBLIC_ACCOUNT)
        and not gdpr_api.has_user_pending_anonymization(user_id)
        and users_models.UserRole.ANONYMIZED not in user.roles
    ):
        kwargs["anonymize_form"] = empty_forms.EmptyForm()
        kwargs["anonymize_public_accounts_dst"] = url_for(".anonymize_public_account", user_id=user.id)

    id_check_histories_desc = _get_id_check_histories_desc(eligibility_history)
    tunnel = _get_tunnel(user, eligibility_history)
    fraud_actions = [_convert_fraud_review_to_fraud_action_dict(review) for review in user.beneficiaryFraudReviews] + [
        _convert_check_item_to_fraud_action_dict(idCheckHistory) for idCheckHistory in id_check_histories_desc
    ]
    fraud_actions_desc = sorted(
        fraud_actions,
        key=lambda action: action["creationDate"],
        reverse=True,
    )

    is_user_expired = users_api.has_profile_expired(user)

    search_form = account_forms.AccountSearchForm()  # values taken from request
    if utils.has_current_user_permission(perm_models.Permissions.MANAGE_ACCOUNT_TAGS):
        tag_account_form = account_forms.TagAccountForm(tags=user.tags)
        kwargs["tag_public_account_form"] = tag_account_form
        kwargs["tag_public_account_dst"] = url_for(".tag_public_account", user_id=user.id)
        search_form.tag.choices = list(tag_account_form.tags.iter_choices())
    else:
        search_form.tag.choices = [(tag.id, str(tag)) for tag in get_user_tags()]

    kwargs.update(user_forms.get_toggle_suspension_args(user, suspension_type=user_forms.SuspensionUserType.PUBLIC))
    return render_template(
        "accounts/get.html",
        search_form=search_form,
        search_dst=url_for(".search_public_accounts"),
        user=user,
        has_changed_email=has_changed_email,
        tunnel=tunnel,
        fraud_actions_desc=fraud_actions_desc,
        credit=domains_credit,
        history=history,
        duplicate_user_id=duplicate_user_id,
        eligibility_history=eligibility_history,
        latest_fraud_check=latest_fraud_check,
        comment_form=account_forms.CommentForm(),
        comment_dst=url_for(".comment_public_account", user_id=user_id),
        bookings=sorted(user.userBookings, key=lambda booking: booking.dateCreated, reverse=True),
        active_tab=request.args.get("active_tab", "registration"),
        show_personal_info=True,
        has_gdpr_extract=has_gdpr_extract(user=user),
        booking_fraudulent_form=account_forms.TagFraudulentBookingsForm(),
        booking_remove_fraudulent_form=empty_forms.EmptyForm(),
        is_user_expired=is_user_expired,
        **kwargs,
    )


def _get_fraud_reviews_desc(
    fraud_reviews: list[subscription_models.BeneficiaryFraudReview],
) -> list[subscription_models.BeneficiaryFraudReview]:
    return sorted(
        fraud_reviews,
        key=lambda r: r.dateReviewed,
        reverse=True,
    )


def _get_id_check_histories_desc(
    eligibility_history: dict[str, serialization.EligibilitySubscriptionHistoryModel],
) -> list[serialization.IdCheckItemModel]:
    return sorted(
        sum([history.idCheckHistory for history in eligibility_history.values()], []),
        key=lambda h: h.dateCreated,
        reverse=True,
    )


class TunnelType(enum.Enum):
    NOT_ELIGIBLE = "not-eligible"
    # Credits v2 tunnels
    AGE18_OLD = "age-18-old"  # age: 18
    UNDERAGE = "underage"  # age: 15(optional), 16(optional), 17(optional)
    UNDERAGE_AGE18 = "underage+age-18"  # age: 15(optional), 16(optional), 17(old) and 18(new)
    UNDERAGE_AGE17 = "underage+age-17"  # age: 15(optional), 16, 17(new)
    UNDERAGE_AGE17_18 = "underage+age-17-18"  # age: 15(optional), 16, 17(new), 18(new)
    UNDERAGE_AGE18_OLD = "underage+age-18-old"  # age: 15(optional), 16(optional), 17(old), 18(old)

    # Credits v3 tunnels
    AGE17 = "age-17"  # means between 17 and 18 years
    AGE18 = "age-18"  # means 18 years and above
    AGE17_18 = "age-17-18"


class RegistrationStepStatus(enum.Enum):
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"


def _get_id_check_age_at_decree_start(user: users_models.User) -> int | None:
    id_checks_birth_date_at_decree_start = [
        fraud_check.get_identity_check_birth_date()
        for fraud_check in user.beneficiaryFraudChecks
        if fraud_check.status == subscription_models.FraudCheckStatus.OK
        and fraud_check.dateCreated < settings.CREDIT_V3_DECREE_DATETIME
    ]
    known_birth_dates_at_decree_start = [
        birth_date for birth_date in id_checks_birth_date_at_decree_start if birth_date is not None
    ]
    if not known_birth_dates_at_decree_start:
        return None

    id_check_birth_date = max(known_birth_dates_at_decree_start)
    return users_utils.get_age_at_date(id_check_birth_date, settings.CREDIT_V3_DECREE_DATETIME, user.departementCode)


def _get_tunnel_type(user: users_models.User) -> TunnelType:
    """
    Tunnel generation schema:

    ————————————————————————————
    Signup at 15 or 16 years old
    ————————————————————————————
    Signup age: 15 or 16 | Age at decree start: < 15 or 16 | Current age: 15 or 16 → Tunnel: not eligible
    Signup age: 15 or 16 | Age at decree start: < 15 or 16 | Current age: 17 → Tunnel: Pass 17
    Signup age: 15 or 16 | Age at decree start: < 15 or 16 | Current age: 18 → Tunnel: Pass 17 / Pass 18

    Signup age: 15 or 16 | Age at decree start: 15 or 16 | Current age: 15 or 16 → Tunnel: Pass 15-17
    Signup age: 15 or 16 | Age at decree start: 15 or 16 | Current age: 17 → Tunnel: Pass 15-17 / Pass 17
    Signup age: 15 or 16 | Age at decree start: 15 or 16 | Current age: 18 → Tunnel: Pass 15-17 / Pass 17 / Pass 18

    Signup age: 15 or 16 | Age at decree start: 17 | Current age: 17 → Tunnel: Pass 15-17 / Pass 17
    Signup age: 15 or 16 | Age at decree start: 17 | Current age: 18 → Tunnel: Pass 15-17 / Pass 17 / Pass 18

    Signup age: 15 or 16 | Age at decree start: 18 | Current age: 18 → Tunnel: Pass 15-17 / Pass 18 (old)

    ——————————————————————
    Signup at 17 years old
    ——————————————————————
    Signup age: 17 | Age at decree start: < 17 | Current age: 17 → Tunnel: Pass 17
    Signup age: 17 | Age at decree start: < 17 | Current age: 18 → Tunnel: Pass 17 / Pass 18

    Signup age: 17 | Age at decree start: 17 | Current age: 17 → Tunnel: Pass 15-17
    Signup age: 17 | Age at decree start: 17 | Current age: 18 → Tunnel: Pass 15-17 / Pass 18

    Signup age: 17 | Age at decree start: 18 | Current age: 18 → Tunnel: Pass 15-17 / Pass 18 (old)

    ——————————————————————
    Signup at 18 years old
    ——————————————————————
    Signup age: 18 | Sign up before decree → Tunnel: Pass 18 (old)
    Signup age: 18 | Sign up after decree → Tunnel: Pass 18
    """
    if user.birth_date is None:
        return TunnelType.NOT_ELIGIBLE

    age_now = user.age
    user_creation_date = user.dateCreated
    age_at_decree_start = users_utils.get_age_at_date(
        birth_date=user.birth_date,
        specified_datetime=settings.CREDIT_V3_DECREE_DATETIME,
        department_code=user.departementCode,
    )
    id_check_age_at_decree_start = _get_id_check_age_at_decree_start(user)
    signup_age = None
    if user_creation_date:
        signup_age = users_utils.get_age_at_date(
            birth_date=user.birth_date,
            specified_datetime=user_creation_date,
            department_code=user.departementCode,
        )

    if not signup_age or not age_now:
        return TunnelType.NOT_ELIGIBLE

    ################################
    # Signup at 15 or 16 years old #
    ################################
    # After decree start
    if signup_age < users_constants.ELIGIBILITY_AGE_17 and user_creation_date >= settings.CREDIT_V3_DECREE_DATETIME:
        if age_now < users_constants.ELIGIBILITY_AGE_17:
            return TunnelType.NOT_ELIGIBLE
        if age_now == users_constants.ELIGIBILITY_AGE_17:
            return TunnelType.AGE17
        if age_now == users_constants.ELIGIBILITY_AGE_18:
            return TunnelType.AGE17_18

    # Decree starts at age 15 or 16
    if signup_age < users_constants.ELIGIBILITY_AGE_17 and age_at_decree_start < users_constants.ELIGIBILITY_AGE_17:
        if age_now < users_constants.ELIGIBILITY_AGE_17:
            return TunnelType.UNDERAGE
        if age_now == users_constants.ELIGIBILITY_AGE_17:
            return TunnelType.UNDERAGE_AGE17
        if age_now == users_constants.ELIGIBILITY_AGE_18:
            return TunnelType.UNDERAGE_AGE17_18

    # Decree at age 17
    if signup_age < users_constants.ELIGIBILITY_AGE_17 and age_at_decree_start == users_constants.ELIGIBILITY_AGE_17:
        if age_now == users_constants.ELIGIBILITY_AGE_17 and id_check_age_at_decree_start is not None:
            return TunnelType.UNDERAGE
        if age_now == users_constants.ELIGIBILITY_AGE_17 and id_check_age_at_decree_start is None:
            return TunnelType.UNDERAGE_AGE17
        if (
            age_now == users_constants.ELIGIBILITY_AGE_18
            and id_check_age_at_decree_start is None
            or (
                id_check_age_at_decree_start is not None
                and id_check_age_at_decree_start < users_constants.ELIGIBILITY_AGE_18
            )
        ):
            return TunnelType.UNDERAGE_AGE18
        if (
            age_now == users_constants.ELIGIBILITY_AGE_18
            and id_check_age_at_decree_start is not None
            and id_check_age_at_decree_start >= users_constants.ELIGIBILITY_AGE_18
        ):
            return TunnelType.UNDERAGE_AGE18_OLD

    # Decree start at age 18
    if signup_age < users_constants.ELIGIBILITY_AGE_17 and age_at_decree_start >= users_constants.ELIGIBILITY_AGE_18:
        if age_now >= users_constants.ELIGIBILITY_AGE_18:
            return TunnelType.UNDERAGE_AGE18_OLD  # old Pass 18

    ##########################
    # Signup at 17 years old #
    ##########################
    # After decree start
    if signup_age == users_constants.ELIGIBILITY_AGE_17 and age_at_decree_start < users_constants.ELIGIBILITY_AGE_17:
        if age_now == users_constants.ELIGIBILITY_AGE_17:
            return TunnelType.AGE17
        if age_now == users_constants.ELIGIBILITY_AGE_18:
            return TunnelType.AGE17_18

    # Decree start at age 17
    if signup_age == users_constants.ELIGIBILITY_AGE_17 and age_at_decree_start == users_constants.ELIGIBILITY_AGE_17:
        if age_now == users_constants.ELIGIBILITY_AGE_17:
            if user_creation_date >= settings.CREDIT_V3_DECREE_DATETIME:
                # After decree start
                return TunnelType.AGE17
            # Before decree start
            return TunnelType.UNDERAGE
        if age_now == users_constants.ELIGIBILITY_AGE_18:
            if user_creation_date >= settings.CREDIT_V3_DECREE_DATETIME:
                return TunnelType.AGE17_18
            if id_check_age_at_decree_start is None:
                return TunnelType.AGE18
            if (
                id_check_age_at_decree_start is not None
                and id_check_age_at_decree_start < users_constants.ELIGIBILITY_AGE_18
            ):
                return TunnelType.UNDERAGE_AGE17_18
            if (
                id_check_age_at_decree_start is not None
                and id_check_age_at_decree_start >= users_constants.ELIGIBILITY_AGE_18
            ):
                return TunnelType.UNDERAGE_AGE18
            return TunnelType.UNDERAGE_AGE18

    # Decree start at age 18
    if signup_age == users_constants.ELIGIBILITY_AGE_17 and age_at_decree_start >= users_constants.ELIGIBILITY_AGE_18:
        if age_now >= users_constants.ELIGIBILITY_AGE_18:
            return TunnelType.UNDERAGE_AGE18_OLD

    ##########################
    # Signup at 18 years old #
    ##########################
    if signup_age == users_constants.ELIGIBILITY_AGE_18:
        if user_creation_date >= settings.CREDIT_V3_DECREE_DATETIME:
            # After decree start
            return TunnelType.AGE18
        # Before decree start
        return TunnelType.AGE18_OLD

    return TunnelType.NOT_ELIGIBLE


def _get_status(status: str) -> RegistrationStepStatus | None:
    if status in (
        subscription_schemas.SubscriptionItemStatus.OK.value,
        subscription_schemas.SubscriptionItemStatus.NOT_APPLICABLE.value,
        subscription_schemas.SubscriptionItemStatus.NOT_ENABLED.value,
        subscription_schemas.SubscriptionItemStatus.SKIPPED.value,
    ):
        return RegistrationStepStatus.SUCCESS

    if status == subscription_schemas.SubscriptionItemStatus.KO.value:
        return RegistrationStepStatus.ERROR

    if status in (
        subscription_schemas.SubscriptionItemStatus.PENDING.value,
        subscription_schemas.SubscriptionItemStatus.SUSPICIOUS.value,
    ):
        return RegistrationStepStatus.WARNING

    return None


class RegistrationStep:
    def __init__(
        self,
        *,
        step_id: int,
        description: str,
        subscription_item_status: str,
        icon: str = "",
        is_active: bool = False,
        is_disabled: bool = False,
    ):
        self.step_id = step_id
        self.description = description
        self.subscription_item_status = subscription_item_status
        self.icon = icon
        self.status = {
            "error": _get_status(subscription_item_status) == RegistrationStepStatus.ERROR,
            "success": _get_status(subscription_item_status) == RegistrationStepStatus.SUCCESS,
            "warning": _get_status(subscription_item_status) == RegistrationStepStatus.WARNING,
            "active": is_active,
            "disabled": is_disabled,
        }

    def __repr__(self) -> str:
        fmt_status = " ".join([f"status[{key}]={value}" for key, value in self.status.items()])
        return (
            f"<RegistrationStep #{self.step_id} '{self.description}' "
            f"subscription_item_status={self.subscription_item_status} "
            f"icon=<{self.icon}> "
            f"{fmt_status}>"
        )

    def __eq__(self, other: object) -> bool | NotImplementedType:
        if not isinstance(other, RegistrationStep):
            raise NotImplementedError()
        return (
            self.step_id == other.step_id
            and self.description == other.description
            and self.subscription_item_status == other.subscription_item_status
            and self.icon == other.icon
            and self.status == other.status
        )


def _get_steps_for_tunnel(
    user: users_models.User, tunnel_type: TunnelType, subscription_item_status: dict
) -> list[RegistrationStep]:
    item_status_15_17 = subscription_item_status[users_models.EligibilityType.UNDERAGE.value]
    item_status_18 = subscription_item_status[users_models.EligibilityType.AGE18.value]
    item_status_17_18 = subscription_item_status[users_models.EligibilityType.AGE17_18.value]

    match tunnel_type:
        case TunnelType.AGE17:
            steps = _get_steps_tunnel_age17(user, item_status_17_18)
        case TunnelType.AGE18:
            steps = _get_steps_tunnel_age18(user, item_status_17_18)
        case TunnelType.AGE18_OLD:
            steps = _get_steps_tunnel_age18_old(user, item_status_18)
        case TunnelType.AGE17_18:
            steps = _get_steps_tunnel_age17_18(user, item_status_17_18)
        case TunnelType.UNDERAGE:
            steps = _get_steps_tunnel_underage(user, item_status_15_17)
        case TunnelType.UNDERAGE_AGE17:
            steps = _get_steps_tunnel_underage_age17(user, item_status_15_17, item_status_17_18)
        case TunnelType.UNDERAGE_AGE18_OLD:
            steps = _get_steps_tunnel_underage_age18_old(user, item_status_15_17, item_status_18)
        case TunnelType.UNDERAGE_AGE18:
            steps = _get_steps_tunnel_underage_age18(user, item_status_15_17, item_status_17_18)
        case TunnelType.UNDERAGE_AGE17_18:
            steps = _get_steps_tunnel_underage_age17_18(user, item_status_15_17, item_status_17_18)
        case _:
            steps = _get_steps_tunnel_unspecified(item_status_15_17, item_status_18, item_status_17_18)

    steps += _get_steps_tunnel_bonus_credit(user)

    if tunnel_type == TunnelType.NOT_ELIGIBLE:
        return steps

    _set_steps_with_active_and_disabled(steps)
    return steps


def _set_steps_with_active_and_disabled(steps: list[RegistrationStep]) -> None:
    for step in reversed(steps):
        if step.subscription_item_status in (
            subscription_schemas.SubscriptionItemStatus.KO.value,
            subscription_schemas.SubscriptionItemStatus.OK.value,
            subscription_schemas.SubscriptionItemStatus.PENDING.value,
            subscription_schemas.SubscriptionItemStatus.SUSPICIOUS.value,
        ):
            step.status["active"] = True
            break
        step.status["disabled"] = True


def _get_steps_tunnel_unspecified(
    item_status_15_17: dict, item_status_18: dict, item_status_17_18: dict
) -> list[RegistrationStep]:
    email_step_key = subscription_schemas.SubscriptionStep.EMAIL_VALIDATION.value
    email_status = (
        item_status_15_17.get(email_step_key)
        or item_status_18.get(email_step_key)
        or item_status_17_18.get(email_step_key)
        or subscription_schemas.SubscriptionItemStatus.PENDING.value
    )

    steps = [
        RegistrationStep(
            step_id=1,
            description=subscription_schemas.SubscriptionStep.EMAIL_VALIDATION.value,
            subscription_item_status=email_status,
            icon="bi-envelope",
        ),
        RegistrationStep(
            step_id=2,
            description=TunnelType.NOT_ELIGIBLE.value,
            subscription_item_status=email_status,
            icon="bi-question-circle",
            is_disabled=True,
        ),
    ]
    return steps


def _get_steps_tunnel_underage_age17(
    user: users_models.User, item_status_15_17: dict, item_status_17_18: dict
) -> list[RegistrationStep]:
    steps = [
        RegistrationStep(
            step_id=1,
            description=subscription_schemas.SubscriptionStep.EMAIL_VALIDATION.value,
            subscription_item_status=item_status_15_17[subscription_schemas.SubscriptionStep.EMAIL_VALIDATION.value],
            icon="bi-envelope",
        ),
        RegistrationStep(
            step_id=2,
            description=subscription_schemas.SubscriptionStep.PROFILE_COMPLETION.value,
            subscription_item_status=item_status_15_17[subscription_schemas.SubscriptionStep.PROFILE_COMPLETION.value],
            icon="bi-universal-access",
        ),
        RegistrationStep(
            step_id=3,
            description=subscription_schemas.SubscriptionStep.IDENTITY_CHECK.value,
            subscription_item_status=item_status_15_17[subscription_schemas.SubscriptionStep.IDENTITY_CHECK.value],
            icon="bi-person-bounding-box",
        ),
        RegistrationStep(
            step_id=4,
            description=subscription_schemas.SubscriptionStep.HONOR_STATEMENT.value,
            subscription_item_status=item_status_15_17[subscription_schemas.SubscriptionStep.HONOR_STATEMENT.value],
            icon="bi-file-text",
        ),
        RegistrationStep(
            step_id=5,
            description=users_models.EligibilityType.UNDERAGE.value,
            subscription_item_status=(
                subscription_schemas.SubscriptionItemStatus.OK.value
                if user.received_pass_15_17
                else subscription_schemas.SubscriptionItemStatus.VOID.value
            ),
            icon="bi-rocket-takeoff",
        ),
        RegistrationStep(
            step_id=6,
            description=subscription_schemas.SubscriptionStep.IDENTITY_CHECK.value,
            subscription_item_status=item_status_17_18[subscription_schemas.SubscriptionStep.IDENTITY_CHECK.value],
            icon="bi-person-bounding-box",
        ),
        RegistrationStep(
            step_id=7,
            description=subscription_schemas.SubscriptionStep.HONOR_STATEMENT.value,
            subscription_item_status=item_status_17_18[subscription_schemas.SubscriptionStep.HONOR_STATEMENT.value],
            icon="bi-file-text",
        ),
        RegistrationStep(
            step_id=8,
            description="Pass 17",
            subscription_item_status=(
                subscription_schemas.SubscriptionItemStatus.OK.value
                if user.received_pass_17_18
                else subscription_schemas.SubscriptionItemStatus.VOID.value
            ),
            icon="bi-rocket-takeoff",
        ),
    ]
    return steps


def _get_steps_tunnel_underage_age17_18(
    user: users_models.User, item_status_15_17: dict, item_status_17_18: dict
) -> list[RegistrationStep]:
    steps = [
        RegistrationStep(
            step_id=1,
            description=subscription_schemas.SubscriptionStep.EMAIL_VALIDATION.value,
            subscription_item_status=item_status_15_17[subscription_schemas.SubscriptionStep.EMAIL_VALIDATION.value],
            icon="bi-envelope",
        ),
        RegistrationStep(
            step_id=2,
            description=subscription_schemas.SubscriptionStep.PROFILE_COMPLETION.value,
            subscription_item_status=item_status_15_17[subscription_schemas.SubscriptionStep.PROFILE_COMPLETION.value],
            icon="bi-universal-access",
        ),
        RegistrationStep(
            step_id=3,
            description=subscription_schemas.SubscriptionStep.IDENTITY_CHECK.value,
            subscription_item_status=item_status_15_17[subscription_schemas.SubscriptionStep.IDENTITY_CHECK.value],
            icon="bi-person-bounding-box",
        ),
        RegistrationStep(
            step_id=4,
            description=subscription_schemas.SubscriptionStep.HONOR_STATEMENT.value,
            subscription_item_status=item_status_15_17[subscription_schemas.SubscriptionStep.HONOR_STATEMENT.value],
            icon="bi-file-text",
        ),
        RegistrationStep(
            step_id=5,
            description=users_models.EligibilityType.UNDERAGE.value,
            subscription_item_status=(
                subscription_schemas.SubscriptionItemStatus.OK.value
                if user.received_pass_15_17
                else subscription_schemas.SubscriptionItemStatus.VOID.value
            ),
            icon="bi-rocket-takeoff",
        ),
        RegistrationStep(
            step_id=6,
            description="age-17",
            subscription_item_status=(
                subscription_schemas.SubscriptionItemStatus.OK.value
                if user.received_pass_17_18
                else subscription_schemas.SubscriptionItemStatus.VOID.value
            ),
            icon="bi-file-text",
        ),
        RegistrationStep(
            step_id=7,
            description=subscription_schemas.SubscriptionStep.PHONE_VALIDATION.value,
            subscription_item_status=item_status_17_18[subscription_schemas.SubscriptionStep.PHONE_VALIDATION.value],
            icon="bi-telephone",
        ),
        RegistrationStep(
            step_id=8,
            description=subscription_schemas.SubscriptionStep.PROFILE_COMPLETION.value,
            subscription_item_status=item_status_17_18[subscription_schemas.SubscriptionStep.PROFILE_COMPLETION.value],
            icon="bi-universal-access",
        ),
        RegistrationStep(
            step_id=9,
            description=subscription_schemas.SubscriptionStep.IDENTITY_CHECK.value,
            subscription_item_status=item_status_17_18[subscription_schemas.SubscriptionStep.IDENTITY_CHECK.value],
            icon="bi-person-bounding-box",
        ),
        RegistrationStep(
            step_id=10,
            description=subscription_schemas.SubscriptionStep.HONOR_STATEMENT.value,
            subscription_item_status=item_status_17_18[subscription_schemas.SubscriptionStep.HONOR_STATEMENT.value],
            icon="bi-file-text",
        ),
        RegistrationStep(
            step_id=11,
            description="age-18",
            subscription_item_status=(
                subscription_schemas.SubscriptionItemStatus.OK.value
                if user.received_pass_18_v3
                else subscription_schemas.SubscriptionItemStatus.VOID.value
            ),
            icon="bi-file-text",
        ),
    ]
    return steps


def _get_steps_tunnel_underage_age18(
    user: users_models.User, item_status_15_17: dict, item_status_17_18: dict
) -> list[RegistrationStep]:
    steps = [
        RegistrationStep(
            step_id=1,
            description=subscription_schemas.SubscriptionStep.EMAIL_VALIDATION.value,
            subscription_item_status=item_status_15_17[subscription_schemas.SubscriptionStep.EMAIL_VALIDATION.value],
            icon="bi-envelope",
        ),
        RegistrationStep(
            step_id=2,
            description=subscription_schemas.SubscriptionStep.PROFILE_COMPLETION.value,
            subscription_item_status=item_status_15_17[subscription_schemas.SubscriptionStep.PROFILE_COMPLETION.value],
            icon="bi-universal-access",
        ),
        RegistrationStep(
            step_id=3,
            description=subscription_schemas.SubscriptionStep.IDENTITY_CHECK.value,
            subscription_item_status=item_status_15_17[subscription_schemas.SubscriptionStep.IDENTITY_CHECK.value],
            icon="bi-person-bounding-box",
        ),
        RegistrationStep(
            step_id=4,
            description=subscription_schemas.SubscriptionStep.HONOR_STATEMENT.value,
            subscription_item_status=item_status_15_17[subscription_schemas.SubscriptionStep.HONOR_STATEMENT.value],
            icon="bi-file-text",
        ),
        RegistrationStep(
            step_id=5,
            description=users_models.EligibilityType.UNDERAGE.value,
            subscription_item_status=(
                subscription_schemas.SubscriptionItemStatus.OK.value
                if user.received_pass_15_17
                else subscription_schemas.SubscriptionItemStatus.VOID.value
            ),
            icon="bi-rocket-takeoff",
        ),
        RegistrationStep(
            step_id=6,
            description=subscription_schemas.SubscriptionStep.PHONE_VALIDATION.value,
            subscription_item_status=item_status_17_18[subscription_schemas.SubscriptionStep.PHONE_VALIDATION.value],
            icon="bi-telephone",
        ),
        RegistrationStep(
            step_id=7,
            description=subscription_schemas.SubscriptionStep.PROFILE_COMPLETION.value,
            subscription_item_status=item_status_17_18[subscription_schemas.SubscriptionStep.PROFILE_COMPLETION.value],
            icon="bi-universal-access",
        ),
        RegistrationStep(
            step_id=8,
            description=subscription_schemas.SubscriptionStep.IDENTITY_CHECK.value,
            subscription_item_status=item_status_17_18[subscription_schemas.SubscriptionStep.IDENTITY_CHECK.value],
            icon="bi-person-bounding-box",
        ),
        RegistrationStep(
            step_id=9,
            description=subscription_schemas.SubscriptionStep.HONOR_STATEMENT.value,
            subscription_item_status=item_status_17_18[subscription_schemas.SubscriptionStep.HONOR_STATEMENT.value],
            icon="bi-file-text",
        ),
        RegistrationStep(
            step_id=10,
            description="age-18",
            subscription_item_status=(
                subscription_schemas.SubscriptionItemStatus.OK.value
                if user.received_pass_18_v3
                else subscription_schemas.SubscriptionItemStatus.VOID.value
            ),
            icon="bi-file-text",
        ),
    ]
    return steps


def _get_steps_tunnel_underage_age18_old(
    user: users_models.User, item_status_15_17: dict, item_status_18: dict
) -> list[RegistrationStep]:
    steps = [
        RegistrationStep(
            step_id=1,
            description=subscription_schemas.SubscriptionStep.EMAIL_VALIDATION.value,
            subscription_item_status=item_status_15_17[subscription_schemas.SubscriptionStep.EMAIL_VALIDATION.value],
            icon="bi-envelope",
        ),
        RegistrationStep(
            step_id=2,
            description=subscription_schemas.SubscriptionStep.PROFILE_COMPLETION.value,
            subscription_item_status=item_status_15_17[subscription_schemas.SubscriptionStep.PROFILE_COMPLETION.value],
            icon="bi-universal-access",
        ),
        RegistrationStep(
            step_id=3,
            description=subscription_schemas.SubscriptionStep.IDENTITY_CHECK.value,
            subscription_item_status=item_status_15_17[subscription_schemas.SubscriptionStep.IDENTITY_CHECK.value],
            icon="bi-person-bounding-box",
        ),
        RegistrationStep(
            step_id=4,
            description=subscription_schemas.SubscriptionStep.HONOR_STATEMENT.value,
            subscription_item_status=item_status_15_17[subscription_schemas.SubscriptionStep.HONOR_STATEMENT.value],
            icon="bi-file-text",
        ),
        RegistrationStep(
            step_id=5,
            description=users_models.EligibilityType.UNDERAGE.value,
            subscription_item_status=(
                subscription_schemas.SubscriptionItemStatus.OK.value
                if user.received_pass_15_17
                else subscription_schemas.SubscriptionItemStatus.VOID.value
            ),
            icon="bi-rocket-takeoff",
        ),
        RegistrationStep(
            step_id=6,
            description=subscription_schemas.SubscriptionStep.PHONE_VALIDATION.value,
            subscription_item_status=item_status_18[subscription_schemas.SubscriptionStep.PHONE_VALIDATION.value],
            icon="bi-telephone",
        ),
        RegistrationStep(
            step_id=7,
            description=subscription_schemas.SubscriptionStep.PROFILE_COMPLETION.value,
            subscription_item_status=item_status_18[subscription_schemas.SubscriptionStep.PROFILE_COMPLETION.value],
            icon="bi-universal-access",
        ),
        RegistrationStep(
            step_id=8,
            description=subscription_schemas.SubscriptionStep.IDENTITY_CHECK.value,
            subscription_item_status=item_status_18[subscription_schemas.SubscriptionStep.IDENTITY_CHECK.value],
            icon="bi-person-bounding-box",
        ),
        RegistrationStep(
            step_id=9,
            description=subscription_schemas.SubscriptionStep.HONOR_STATEMENT.value,
            subscription_item_status=item_status_18[subscription_schemas.SubscriptionStep.HONOR_STATEMENT.value],
            icon="bi-file-text",
        ),
        RegistrationStep(
            step_id=10,
            description="Ancien Pass 18",
            subscription_item_status=(
                subscription_schemas.SubscriptionItemStatus.OK.value
                if user.received_pass_18
                else subscription_schemas.SubscriptionItemStatus.VOID.value
            ),
            icon="bi-file-text",
        ),
    ]
    return steps


def _get_steps_tunnel_age17(user: users_models.User, item_status_17_18: dict) -> list[RegistrationStep]:
    steps = [
        RegistrationStep(
            step_id=1,
            description=subscription_schemas.SubscriptionStep.EMAIL_VALIDATION.value,
            subscription_item_status=item_status_17_18[subscription_schemas.SubscriptionStep.EMAIL_VALIDATION.value],
            icon="bi-envelope",
        ),
        RegistrationStep(
            step_id=2,
            description=subscription_schemas.SubscriptionStep.PROFILE_COMPLETION.value,
            subscription_item_status=item_status_17_18[subscription_schemas.SubscriptionStep.PROFILE_COMPLETION.value],
            icon="bi-universal-access",
        ),
        RegistrationStep(
            step_id=3,
            description=subscription_schemas.SubscriptionStep.IDENTITY_CHECK.value,
            subscription_item_status=item_status_17_18[subscription_schemas.SubscriptionStep.IDENTITY_CHECK.value],
            icon="bi-person-bounding-box",
        ),
        RegistrationStep(
            step_id=4,
            description=subscription_schemas.SubscriptionStep.HONOR_STATEMENT.value,
            subscription_item_status=item_status_17_18[subscription_schemas.SubscriptionStep.HONOR_STATEMENT.value],
            icon="bi-file-text",
        ),
        RegistrationStep(
            step_id=5,
            description="Pass 17",
            subscription_item_status=(
                subscription_schemas.SubscriptionItemStatus.OK.value
                if user.received_pass_17_18
                else subscription_schemas.SubscriptionItemStatus.VOID.value
            ),
        ),
    ]
    return steps


def _get_steps_tunnel_age17_18(user: users_models.User, item_status_17_18: dict) -> list[RegistrationStep]:
    steps = [
        RegistrationStep(
            step_id=1,
            description=subscription_schemas.SubscriptionStep.EMAIL_VALIDATION.value,
            subscription_item_status=item_status_17_18[subscription_schemas.SubscriptionStep.EMAIL_VALIDATION.value],
            icon="bi-envelope",
        ),
        RegistrationStep(
            step_id=2,
            description=subscription_schemas.SubscriptionStep.PROFILE_COMPLETION.value,
            subscription_item_status=item_status_17_18[subscription_schemas.SubscriptionStep.PROFILE_COMPLETION.value],
            icon="bi-universal-access",
        ),
        RegistrationStep(
            step_id=3,
            description=subscription_schemas.SubscriptionStep.IDENTITY_CHECK.value,
            subscription_item_status=item_status_17_18[subscription_schemas.SubscriptionStep.IDENTITY_CHECK.value],
            icon="bi-person-bounding-box",
        ),
        RegistrationStep(
            step_id=4,
            description=subscription_schemas.SubscriptionStep.HONOR_STATEMENT.value,
            subscription_item_status=item_status_17_18[subscription_schemas.SubscriptionStep.HONOR_STATEMENT.value],
            icon="bi-file-text",
        ),
        RegistrationStep(
            step_id=5,
            description="Pass 17",
            subscription_item_status=(
                subscription_schemas.SubscriptionItemStatus.OK.value
                if user.received_pass_17_18
                else subscription_schemas.SubscriptionItemStatus.VOID.value
            ),
            icon="bi-rocket-takeoff",
        ),
        RegistrationStep(
            step_id=6,
            description=subscription_schemas.SubscriptionStep.PHONE_VALIDATION.value,
            subscription_item_status=item_status_17_18[subscription_schemas.SubscriptionStep.PHONE_VALIDATION.value],
            icon="bi-telephone",
        ),
        RegistrationStep(
            step_id=7,
            description=subscription_schemas.SubscriptionStep.PROFILE_COMPLETION.value,
            subscription_item_status=item_status_17_18[subscription_schemas.SubscriptionStep.PROFILE_COMPLETION.value],
            icon="bi-universal-access",
        ),
        RegistrationStep(
            step_id=8,
            description=subscription_schemas.SubscriptionStep.IDENTITY_CHECK.value,
            subscription_item_status=item_status_17_18[subscription_schemas.SubscriptionStep.IDENTITY_CHECK.value],
            icon="bi-person-bounding-box",
        ),
        RegistrationStep(
            step_id=9,
            description=subscription_schemas.SubscriptionStep.HONOR_STATEMENT.value,
            subscription_item_status=item_status_17_18[subscription_schemas.SubscriptionStep.HONOR_STATEMENT.value],
            icon="bi-file-text",
        ),
        RegistrationStep(
            step_id=10,
            description="Pass 18",
            subscription_item_status=(
                subscription_schemas.SubscriptionItemStatus.OK.value
                if user.received_pass_18_v3
                else subscription_schemas.SubscriptionItemStatus.VOID.value
            ),
            icon="bi-rocket-takeoff",
        ),
    ]
    return steps


def _get_steps_tunnel_age18(user: users_models.User, item_status_17_18: dict) -> list[RegistrationStep]:
    steps = [
        RegistrationStep(
            step_id=1,
            description=subscription_schemas.SubscriptionStep.EMAIL_VALIDATION.value,
            subscription_item_status=item_status_17_18[subscription_schemas.SubscriptionStep.EMAIL_VALIDATION.value],
            icon="bi-envelope",
        ),
        RegistrationStep(
            step_id=2,
            description=subscription_schemas.SubscriptionStep.PHONE_VALIDATION.value,
            subscription_item_status=item_status_17_18[subscription_schemas.SubscriptionStep.PHONE_VALIDATION.value],
            icon="bi-telephone",
        ),
        RegistrationStep(
            step_id=3,
            description=subscription_schemas.SubscriptionStep.PROFILE_COMPLETION.value,
            subscription_item_status=item_status_17_18[subscription_schemas.SubscriptionStep.PROFILE_COMPLETION.value],
            icon="bi-universal-access",
        ),
        RegistrationStep(
            step_id=4,
            description=subscription_schemas.SubscriptionStep.IDENTITY_CHECK.value,
            subscription_item_status=item_status_17_18[subscription_schemas.SubscriptionStep.IDENTITY_CHECK.value],
            icon="bi-person-bounding-box",
        ),
        RegistrationStep(
            step_id=5,
            description=subscription_schemas.SubscriptionStep.HONOR_STATEMENT.value,
            subscription_item_status=item_status_17_18[subscription_schemas.SubscriptionStep.HONOR_STATEMENT.value],
            icon="bi-file-text",
        ),
        RegistrationStep(
            step_id=6,
            description="Pass 18",
            subscription_item_status=(
                subscription_schemas.SubscriptionItemStatus.OK.value
                if user.received_pass_18_v3
                else subscription_schemas.SubscriptionItemStatus.VOID.value
            ),
            icon="bi-rocket-takeoff",
        ),
    ]
    return steps


def _get_steps_tunnel_age18_old(user: users_models.User, item_status_18: dict) -> list[RegistrationStep]:
    steps = [
        RegistrationStep(
            step_id=1,
            description=subscription_schemas.SubscriptionStep.EMAIL_VALIDATION.value,
            subscription_item_status=item_status_18[subscription_schemas.SubscriptionStep.EMAIL_VALIDATION.value],
            icon="bi-envelope",
        ),
        RegistrationStep(
            step_id=2,
            description=subscription_schemas.SubscriptionStep.PHONE_VALIDATION.value,
            subscription_item_status=item_status_18[subscription_schemas.SubscriptionStep.PHONE_VALIDATION.value],
            icon="bi-telephone",
        ),
        RegistrationStep(
            step_id=3,
            description=subscription_schemas.SubscriptionStep.PROFILE_COMPLETION.value,
            subscription_item_status=item_status_18[subscription_schemas.SubscriptionStep.PROFILE_COMPLETION.value],
            icon="bi-universal-access",
        ),
        RegistrationStep(
            step_id=4,
            description=subscription_schemas.SubscriptionStep.IDENTITY_CHECK.value,
            subscription_item_status=item_status_18[subscription_schemas.SubscriptionStep.IDENTITY_CHECK.value],
            icon="bi-person-bounding-box",
        ),
        RegistrationStep(
            step_id=5,
            description=subscription_schemas.SubscriptionStep.HONOR_STATEMENT.value,
            subscription_item_status=item_status_18[subscription_schemas.SubscriptionStep.HONOR_STATEMENT.value],
            icon="bi-file-text",
        ),
        RegistrationStep(
            step_id=6,
            description="Ancien Pass 18",
            subscription_item_status=(
                subscription_schemas.SubscriptionItemStatus.OK.value
                if user.received_pass_18
                else subscription_schemas.SubscriptionItemStatus.VOID.value
            ),
            icon="bi-rocket-takeoff",
        ),
    ]
    return steps


def _get_steps_tunnel_underage(user: users_models.User, item_status_15_17: dict) -> list[RegistrationStep]:
    steps = [
        RegistrationStep(
            step_id=1,
            description=subscription_schemas.SubscriptionStep.EMAIL_VALIDATION.value,
            subscription_item_status=item_status_15_17[subscription_schemas.SubscriptionStep.EMAIL_VALIDATION.value],
            icon="bi-envelope",
        ),
        RegistrationStep(
            step_id=2,
            description=subscription_schemas.SubscriptionStep.PROFILE_COMPLETION.value,
            subscription_item_status=item_status_15_17[subscription_schemas.SubscriptionStep.PROFILE_COMPLETION.value],
            icon="bi-universal-access",
        ),
        RegistrationStep(
            step_id=3,
            description=subscription_schemas.SubscriptionStep.IDENTITY_CHECK.value,
            subscription_item_status=item_status_15_17[subscription_schemas.SubscriptionStep.IDENTITY_CHECK.value],
            icon="bi-person-bounding-box",
        ),
        RegistrationStep(
            step_id=4,
            description=subscription_schemas.SubscriptionStep.HONOR_STATEMENT.value,
            subscription_item_status=item_status_15_17[subscription_schemas.SubscriptionStep.HONOR_STATEMENT.value],
            icon="bi-file-text",
        ),
        RegistrationStep(
            step_id=5,
            description="Ancien Pass 15-17",
            subscription_item_status=(
                subscription_schemas.SubscriptionItemStatus.OK.value
                if user.received_pass_15_17
                else subscription_schemas.SubscriptionItemStatus.VOID.value
            ),
            icon="bi-rocket-takeoff",
        ),
    ]
    return steps


def _get_steps_tunnel_bonus_credit(user: users_models.User) -> list[RegistrationStep]:
    bonus_fraud_checks = users_api.get_qf_bonus_credit_fraud_checks(user)
    if not bonus_fraud_checks:
        return []

    bonus_fraud_check = bonus_fraud_checks[-1]
    match bonus_fraud_check.status:
        case subscription_models.FraudCheckStatus.OK:
            status = subscription_schemas.SubscriptionItemStatus.OK
        case subscription_models.FraudCheckStatus.KO:
            status = subscription_schemas.SubscriptionItemStatus.KO
        case subscription_models.FraudCheckStatus.STARTED | subscription_models.FraudCheckStatus.PENDING:
            status = subscription_schemas.SubscriptionItemStatus.PENDING
        case _:
            status = subscription_schemas.SubscriptionItemStatus.TODO

    return [
        RegistrationStep(
            step_id=11,
            description="Demande de bonification",
            subscription_item_status=status.value,
            icon="bi-envelope-paper",
        ),
        RegistrationStep(
            step_id=12,
            description="Bonification",
            subscription_item_status=(
                subscription_schemas.SubscriptionItemStatus.OK.value
                if user.received_bonus_credit
                else subscription_schemas.SubscriptionItemStatus.VOID.value
            ),
            icon="bi-patch-plus",
        ),
    ]


def _get_tunnel(
    user: users_models.User,
    eligibility_history: dict[str, serialization.EligibilitySubscriptionHistoryModel],
) -> dict:
    subscription_item_status = _get_subscription_item_status_by_eligibility(eligibility_history)
    tunnel_type = _get_tunnel_type(user)
    steps = _get_steps_for_tunnel(user, tunnel_type, subscription_item_status)
    progress = _get_progress(steps)
    tunnel = {
        "type": tunnel_type,
        "progress": progress,
        "steps": steps,
    }
    return tunnel


def _get_subscription_item_status_by_eligibility(
    eligibility_history: dict[str, serialization.EligibilitySubscriptionHistoryModel],
) -> dict[str, dict]:
    subscription_item_status: dict[str, dict] = {
        users_models.EligibilityType.UNDERAGE.value: {},
        users_models.EligibilityType.AGE18.value: {},
        users_models.EligibilityType.AGE17_18.value: {},
    }
    for key, value in eligibility_history.items():
        for item in value.subscriptionItems:
            if key in [
                users_models.EligibilityType.UNDERAGE.value,
                users_models.EligibilityType.AGE18.value,
                users_models.EligibilityType.AGE17_18.value,
            ]:
                subscription_item_status[key][item.type] = item.status
    return subscription_item_status


def _get_progress(steps: list[RegistrationStep]) -> float:
    active_step_index = next((index for (index, s) in enumerate(steps) if s.status["active"]), None)
    progress = active_step_index * (100 / (len(steps) - 1)) if active_step_index else 0
    return progress


@public_accounts_blueprint.route("/<int:user_id>", methods=["GET"])
@utils.permission_required(perm_models.Permissions.READ_PUBLIC_ACCOUNT)
def get_public_account(user_id: int) -> utils.BackofficeResponse:
    return render_public_account_details(user_id)


@public_accounts_blueprint.route("/<int:user_id>", methods=["POST"])
@utils.permission_required(perm_models.Permissions.MANAGE_PUBLIC_ACCOUNT)
def update_public_account(user_id: int) -> utils.BackofficeResponse:
    user = (
        db.session.query(users_models.User)
        .filter_by(id=user_id)
        .populate_existing()
        .with_for_update(key_share=True)
        .one_or_none()
    )
    if not user:
        raise NotFound()

    form = account_forms.EditAccountForm()
    if not form.validate():
        flash("Le formulaire n'est pas valide", "warning")
        return render_public_account_details(user_id, form), 400

    try:
        # Use atomic because render_public_account_details makes select queries in exceptions after rollback which
        # returns to savepoint.
        with atomic():
            snapshot = users_api.update_user_info(
                user,
                author=current_user,
                first_name=form.first_name.data,
                last_name=form.last_name.data,
                validated_birth_date=form.birth_date.data,
                phone_number=form.phone_number.data,
                id_piece_number=form.id_piece_number.data,
                address=form.street.data,
                postal_code=form.postal_code.data,
                city=form.city.data,
                commit=False,
                marketing_email_subscription=form.marketing_email_subscription.data,
            )
            db.session.flush()
    except phone_validation_exceptions.InvalidPhoneNumber:
        flash("Le numéro de téléphone est invalide", "warning")
        return render_public_account_details(user_id, form), 400
    except sa.exc.IntegrityError as exc:
        message = str(exc)
        if "user_idPieceNumber_key" in message:
            flash(
                Markup(
                    "Le numéro de pièce d'identité <b>{id_piece_number}</b> est déjà associé à un autre compte utilisateur."
                ).format(id_piece_number=form.id_piece_number.data),
                "warning",
            )
        else:
            flash(Markup("Une erreur s'est produite : {message}").format(message=message), "warning")
        return render_public_account_details(user_id, form), 400

    email_changed = bool(form.email.data and form.email.data != email_utils.sanitize_email(user.email))
    if email_changed:
        # Do not log email change in snapshot, since it is already logged in user_email_history table
        try:
            email_update.full_email_update_by_admin(user, form.email.data)
        except users_exceptions.EmailExistsError:
            form.email.errors.append("L'email est déjà associé à un autre utilisateur")
            flash("L'email est déjà associé à un autre utilisateur", "warning")
            return render_public_account_details(user_id, form), 400

    snapshot.add_action()
    db.session.flush()

    if email_changed:
        # TODO (prouzet) old email should also be updated, but there is no update_external_user by email
        external_attributes_api.update_external_user(user)

    modified_info = snapshot.to_dict()
    if user.isActive and send_beneficiary_personal_data_updated(
        user,
        is_first_name_updated=bool(modified_info.get("firstName", {}).get("new_info")),
        is_last_name_updated=bool(modified_info.get("lastName", {}).get("new_info")),
        is_email_updated=email_changed,
        is_phone_number_updated=bool(modified_info.get("phoneNumber", {}).get("new_info")),
    ):
        flash(
            Markup("Les informations ont été mises à jour, un mail de confirmation est envoyé à <b>{email}</b>").format(
                email=user.email
            ),
            "success",
        )
    else:
        flash("Les informations ont été mises à jour", "success")

    return redirect(get_public_account_link(user_id, active_tab="history"), code=303)


@public_accounts_blueprint.route("/<int:user_id>/resend-validation-email", methods=["POST"])
@utils.permission_required(perm_models.Permissions.MANAGE_PUBLIC_ACCOUNT)
def resend_validation_email(user_id: int) -> utils.BackofficeResponse:
    user = db.session.query(users_models.User).filter_by(id=user_id).one_or_none()
    if not user:
        raise NotFound()

    if user.has_admin_role or user.has_pro_role:
        flash("Cette action n'est pas supportée pour les utilisateurs admin ou pro", "warning")
    elif user.isEmailValidated:
        flash("L'adresse email est déjà validée", "warning")
    else:
        users_api.request_email_confirmation(user)
        flash("L'email de validation a été envoyé", "success")

    return redirect(get_public_account_link(user_id), code=303)


@public_accounts_blueprint.route("/<int:user_id>/validate-phone-number", methods=["POST"])
@utils.permission_required(perm_models.Permissions.MANAGE_PUBLIC_ACCOUNT)
def manually_validate_phone_number(user_id: int) -> utils.BackofficeResponse:
    user = (
        db.session.query(users_models.User)
        .filter_by(id=user_id)
        .populate_existing()
        .with_for_update(key_share=True)
        .one_or_none()
    )
    if not user:
        raise NotFound()

    if not user.phoneNumber:
        flash("L'utilisateur n'a pas de numéro de téléphone", "warning")
        return redirect(get_public_account_link(user_id), code=303)

    user.phoneValidationStatus = users_models.PhoneValidationStatusType.VALIDATED
    db.session.add(user)
    history_api.add_action(history_models.ActionType.USER_PHONE_VALIDATED, author=current_user, user=user)
    db.session.flush()

    try:
        subscription_api.activate_beneficiary_if_no_missing_step(user)
    except (subscription_exceptions.SubscriptionException, users_exceptions.InvalidEligibilityTypeException) as exc:
        mark_transaction_as_invalid()
        flash(
            Markup("Une erreur s'est produite : {message}").format(message=str(exc) or exc.__class__.__name__),
            "warning",
        )
    else:
        users_api.delete_all_users_phone_validation_tokens(user)
        flash("Le numéro de téléphone a été validé", "success")

    return redirect(get_public_account_link(user_id), code=303)


@public_accounts_blueprint.route("/<int:user_id>/send-validation-code", methods=["POST"])
@utils.permission_required(perm_models.Permissions.MANAGE_PUBLIC_ACCOUNT)
def send_validation_code(user_id: int) -> utils.BackofficeResponse:
    user = (
        db.session.query(users_models.User)
        .filter_by(id=user_id)
        .populate_existing()
        .with_for_update(key_share=True)
        .one_or_none()
    )
    if not user:
        raise NotFound()

    if not user.phoneNumber:
        flash("L'utilisateur n'a pas de numéro de téléphone", "warning")
        return redirect(get_public_account_link(user_id), code=303)

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

    return redirect(get_public_account_link(user_id), code=303)


@public_accounts_blueprint.route("/<int:user_id>/review", methods=["POST"])
@utils.permission_required(perm_models.Permissions.BENEFICIARY_MANUAL_REVIEW)
def review_public_account(user_id: int) -> utils.BackofficeResponse:
    user = (
        db.session.query(users_models.User)
        .filter_by(id=user_id)
        .populate_existing()
        .with_for_update(key_share=True)
        .options(sa_orm.selectinload(users_models.User.deposits).selectinload(finance_models.Deposit.recredits))
        .one_or_none()
    )
    if not user:
        raise NotFound()

    form = account_forms.ManualReviewForm()
    if not form.validate():
        flash(utils.build_form_error_msg(form), "warning")
        return redirect(url_for("backoffice_web.public_accounts.get_public_account", user_id=user_id), code=303)

    eligibility = users_models.EligibilityType[form.eligibility.data]
    try:
        if eligibility == users_models.EligibilityType.AGE18 and user.has_underage_beneficiary_role:
            deposit_api.expire_current_deposit_for_user(user=user)
        fraud_api.validate_beneficiary(
            user=user,
            reviewer=current_user,
            reason=form.reason.data,
            review=subscription_models.FraudReviewStatus(form.status.data),
            reviewed_eligibility=eligibility,
        )
    except (fraud_exceptions.FraudException, finance_exceptions.FinanceException, DisabledFeatureError) as exc:
        mark_transaction_as_invalid()
        flash(
            Markup("Une erreur s'est produite : {message}").format(message=str(exc) or exc.__class__.__name__),
            "warning",
        )

    except users_exceptions.InvalidEligibilityTypeException as e:
        mark_transaction_as_invalid()

        if isinstance(e, users_exceptions.UnderageEligibilityWhenAlreadyEighteenException):
            warning_message = "Le compte est déjà majeur (18+) il ne peut pas aussi être bénéficiaire (15-17)"
        elif isinstance(e, users_exceptions.PreDecreeEligibilityWhenPostDecreeBeneficiaryException):
            warning_message = "Le compte est déjà bénéficiaire du Pass 17-18, il ne peut pas aussi être bénéficiaire de l'ancien Pass 15-17 ou 18"
        elif isinstance(e, users_exceptions.MustBePreDecreeEligibilityException):
            warning_message = (
                "Le compte a commencé le parcours d'activation de l'ancien crédit. Il est éligible à l'ancien Pass 18."
            )
        else:
            warning_message = f"L'éligibilité '{eligibility.value}' n'est pas applicable à cet utilisateur"

        flash(warning_message, "warning")

    else:
        flash("Validation réussie", "success")

    return redirect(get_public_account_link(user_id), code=303)


def _fetch_user_for_bonus(user_id: int) -> users_models.User:
    user = (
        db.session.query(users_models.User)
        .filter_by(id=user_id)
        .options(
            sa_orm.joinedload(users_models.User.deposits).joinedload(finance_models.Deposit.recredits),
            sa_orm.lazyload(users_models.User.beneficiaryFraudChecks),
        )
        .one_or_none()
    )
    if not user:
        raise NotFound()
    return user


@public_accounts_blueprint.route("/<int:user_id>/bonus", methods=["GET"])
@utils.permission_required(perm_models.Permissions.REQUEST_BENEFICIARY_BONUS_CREDIT)
def get_request_bonus_credit_form(user_id: int) -> utils.BackofficeResponse:
    user = _fetch_user_for_bonus(user_id)

    if not users_api.get_user_is_eligible_for_bonification(user, is_from_backoffice=True):
        # This should not happen because button should not be displayed, except if the credit is granted in the meantime
        return render_template(
            "components/dynamic/modal_form.html",
            div_id="request-bonus-credit",
            title="Demande de bonification",
            information="Ce compte n'est pas éligible à une bonification.",
        )

    try:
        fraud_checks = users_api.get_qf_bonus_credit_fraud_checks(user)
        content = fraud_checks[-1].source_data()
        assert isinstance(content, bonus_schemas.QuotientFamilialBonusCreditContent)
        custodian = content.custodian
        form = account_forms.BonusCreditRequestForm(
            civility=custodian.gender.name,
            first_names=", ".join(custodian.first_names),
            last_name=custodian.last_name,
            common_name=custodian.common_name,
            birth_date=custodian.birth_date,
            birth_country=custodian.birth_country_cog_code,
            birth_city=[custodian.birth_city_cog_code] if custodian.birth_city_cog_code else None,
        )
        autocomplete.prefill_cities_choice(form.birth_city)
    except Exception:
        # No fraud check or any error => empty form
        form = account_forms.BonusCreditRequestForm()

    return render_template(
        "components/dynamic/modal_form.html",
        title="Demande de bonification",
        information=Markup(
            "Vous pouvez demander la bonification à la place du jeune. "
            "Il faut remplir l'information sur son <b>parent</b>, <b>tuteur légal</b> ou l'<b>organisme qui le prend en charge</b>."
        ),
        form=form,
        dst=url_for("backoffice_web.public_accounts.request_bonus_credit", user_id=user_id),
        div_id="request-bonus-credit",
        button_text="Faire la demande",
        ajax_submit=False,
    )


@public_accounts_blueprint.route("/<int:user_id>/bonus", methods=["POST"])
@utils.permission_required(perm_models.Permissions.REQUEST_BENEFICIARY_BONUS_CREDIT)
def request_bonus_credit(user_id: int) -> utils.BackofficeResponse:
    user = _fetch_user_for_bonus(user_id)

    if not users_api.get_user_is_eligible_for_bonification(user, is_from_backoffice=True):
        # This should not happen because form should not be displayed, except if the credit is granted in the meantime
        flash("Ce compte n'est pas éligible à une bonification", "warning")
        return redirect(get_public_account_link(user_id), code=303)

    form = account_forms.BonusCreditRequestForm()
    if not form.validate():
        flash(utils.build_form_error_msg(form), "warning")
        return redirect(get_public_account_link(user_id), code=303)

    fraud_check = bonus_fraud_api.create_bonus_credit_fraud_check(
        user,
        gender=users_models.GenderEnum[form.civility.data],
        first_names=list(filter(None, re.split(",|;| ", form.first_names.data))),
        last_name=form.last_name.data,
        common_name=form.common_name.data,
        birth_date=form.birth_date.data,
        birth_country_cog_code=form.birth_country.data,
        birth_city_cog_code=form.birth_city.single_data,
        origin=f"{bonus_constants.BACKOFFICE_ORIGIN_START}, User ID {current_user.id}",
    )

    payload = bonus_tasks.GetQuotientFamilialTaskPayload(fraud_check_id=fraud_check.id).model_dump()
    on_commit(partial(bonus_tasks.apply_for_quotient_familial_bonus_task.delay, payload))

    flash("La demande de bonification est en cours.", "success")
    return redirect(get_public_account_link(user_id), code=303)


@public_accounts_blueprint.route("/<int:user_id>/comment", methods=["POST"])
@utils.permission_required(perm_models.Permissions.MANAGE_PUBLIC_ACCOUNT)
def comment_public_account(user_id: int) -> utils.BackofficeResponse:
    user = (
        db.session.query(users_models.User)
        .filter_by(id=user_id)
        .populate_existing()
        .with_for_update(key_share=True, read=True)
        .one_or_none()
    )
    if not user:
        raise NotFound()

    form = account_forms.CommentForm()
    if not form.validate():
        flash(utils.build_form_error_msg(form), "warning")
    else:
        users_api.add_comment_to_user(user=user, author_user=current_user, comment=form.comment.data)
        flash("Le commentaire a été enregistré", "success")

    return redirect(get_public_account_link(user_id, active_tab="history"), code=303)


def get_public_account_link(
    user_id: int, form: account_forms.AccountSearchForm | None = None, **kwargs: typing.Any
) -> str:
    if form and form.q.data:
        kwargs["q"] = form.q.data
    return url_for("backoffice_web.public_accounts.get_public_account", user_id=user_id, **kwargs)


def _get_user_fraud_check_eligibility_types(user: users_models.User) -> list[users_models.EligibilityType]:
    if not user.dateOfBirth:
        return []

    return [
        eligibility_type
        for fraud_check in user.beneficiaryFraudChecks
        if (eligibility_type := serialization.get_fraud_check_eligibility_type(fraud_check))
    ]


def get_eligibility_history(user: users_models.User) -> dict[str, serialization.EligibilitySubscriptionHistoryModel]:
    subscriptions = {}
    eligibility_types = []

    subscription_item_methods = [
        subscription_api.get_email_validation_subscription_item,
        subscription_api.get_profile_completion_subscription_item,
        subscription_api.get_phone_validation_subscription_item,
        subscription_api.get_identity_check_subscription_item,
        subscription_api.get_honor_statement_subscription_item,
    ]
    # Do not show information about eligibility types which are not possible depending on known user age
    if user.birth_date:
        age_at_creation = users_utils.get_age_at_date(user.birth_date, user.dateCreated, user.departementCode)
        age_at_decree_start = users_utils.get_age_at_date(
            birth_date=user.birth_date,
            specified_datetime=settings.CREDIT_V3_DECREE_DATETIME,
            department_code=user.departementCode,
        )
        age_now = user.age
        assert age_now is not None  # helps mypy
        fraud_eligibility_types = _get_user_fraud_check_eligibility_types(user)

        if (users_models.EligibilityType.UNDERAGE in fraud_eligibility_types) or (
            user.dateCreated < settings.CREDIT_V3_DECREE_DATETIME
            and age_at_creation < users_constants.ELIGIBILITY_AGE_18
        ):
            eligibility_types.append(users_models.EligibilityType.UNDERAGE)

        if (
            (users_models.EligibilityType.AGE17_18 in fraud_eligibility_types)
            or (age_at_decree_start <= users_constants.ELIGIBILITY_AGE_17)
            or (
                age_at_creation >= users_constants.ELIGIBILITY_AGE_17
                and user.dateCreated >= settings.CREDIT_V3_DECREE_DATETIME
            )
        ):
            eligibility_types.append(users_models.EligibilityType.AGE17_18)

        if (users_models.EligibilityType.AGE18 in fraud_eligibility_types) or (
            age_at_decree_start >= users_constants.ELIGIBILITY_AGE_18 and age_now >= users_constants.ELIGIBILITY_AGE_18
        ):
            eligibility_types.append(users_models.EligibilityType.AGE18)

    else:
        # Profile completion step not reached yet; can't guess eligibility, display all
        eligibility_types = [
            users_models.EligibilityType.UNDERAGE,
            users_models.EligibilityType.AGE17_18,
            users_models.EligibilityType.AGE18,
        ]

    for eligibility in eligibility_types:
        subscriptions[eligibility.value] = serialization.EligibilitySubscriptionHistoryModel(
            subscriptionItems=[
                serialization.SubscriptionItemModel.from_orm(method(user, eligibility))
                for method in subscription_item_methods
            ],
            idCheckHistory=[
                serialization.IdCheckItemModel.build(fraud_check)
                for fraud_check in user.beneficiaryFraudChecks
                if serialization.get_fraud_check_eligibility_type(fraud_check) == eligibility
            ],
        )

    return subscriptions


def _get_latest_fraud_check(
    eligibility_history: dict[str, serialization.EligibilitySubscriptionHistoryModel],
    check_types: list[subscription_models.FraudCheckType],
) -> serialization.IdCheckItemModel | None:
    latest_fraud_check = None
    check_list = []
    for history in eligibility_history.values():
        for idCheckItem in history.idCheckHistory:
            if idCheckItem.type in [check_type.value for check_type in check_types]:
                check_list.append(idCheckItem)
    if check_list:
        check_list = sorted(check_list, key=lambda idCheckItem: idCheckItem.dateCreated, reverse=True)
        latest_fraud_check = check_list[0]
    return latest_fraud_check


def _get_duplicate_fraud_history(
    eligibility_history: dict[str, serialization.EligibilitySubscriptionHistoryModel],
) -> str | None:
    reason_codes_for_duplicates = {
        subscription_models.FraudReasonCode.DUPLICATE_USER.value,
        subscription_models.FraudReasonCode.DUPLICATE_ID_PIECE_NUMBER.value,
    }
    for history_item in eligibility_history.values():
        check_history_items = sorted(history_item.idCheckHistory, key=attrgetter("dateCreated"), reverse=True)
        for check_history in check_history_items:
            reason_codes = set(check_history.reasonCodes or [])

            if reason_codes.intersection(reason_codes_for_duplicates):
                if check_history.reason:
                    id_searched = re.search(r"\s(\d+)\D*$", check_history.reason)
                    if id_searched:
                        return id_searched.group(1)
    return None


def get_public_account_history(
    user: users_models.User, bo_user: users_models.User | None = None
) -> list[serialization.AccountAction | history_models.ActionHistory]:
    # All data should have been joinloaded with user
    history: list[history_models.ActionHistory | serialization.AccountAction] = list(user.action_history)

    if history_models.ActionType.USER_CREATED not in (action.actionType for action in user.action_history):
        history.append(serialization.AccountCreatedAction(user))

    for change in user.email_history:
        history.append(serialization.EmailChangeAction(change))

    for fraud_check in user.beneficiaryFraudChecks:
        history.append(serialization.FraudCheckAction(fraud_check, bo_user))

    for review in user.beneficiaryFraudReviews:
        history.append(serialization.ReviewAction(review))

    for import_ in user.beneficiaryImports:
        for status in import_.statuses:
            history.append(serialization.ImportStatusAction(import_, status))

    for deposit in user.deposits:
        history.append(serialization.DepositAction(deposit))
        initial_recredit = deposit.initial_recredit
        for recredit in deposit.recredits:
            if recredit != initial_recredit:
                history.append(serialization.RecreditAction(recredit))

    history = sorted(history, key=lambda item: item.actionDate or datetime.datetime.min, reverse=True)

    return history


@public_accounts_blueprint.route("/<int:user_id>/activity", methods=["GET"])
def get_public_account_activity(user_id: int) -> utils.BackofficeResponse:
    activity: list[serialization.BeneficiaryActivity] = []

    special_event_responses = (
        db.session.query(
            operations_models.SpecialEventResponse.id,
            operations_models.SpecialEventResponse.dateSubmitted,
            operations_models.SpecialEventResponse.status,
            operations_models.SpecialEventResponse.eventId,
            operations_models.SpecialEvent.title.label("title"),
        )
        .select_from(operations_models.SpecialEventResponse)
        .join(operations_models.SpecialEvent)
        .filter(operations_models.SpecialEventResponse.userId == user_id)
    ).all()

    for special_event_response in special_event_responses:
        activity.append(serialization.SpecialEventActivity(special_event_response))

    chronicles = (
        db.session.query(
            chronicles_models.Chronicle.id,
            chronicles_models.Chronicle.dateCreated,
            chronicles_models.Chronicle.productIdentifier,
            chronicles_models.Chronicle.isPublished,
            sa.func.coalesce(
                offers_models.Product.name,
                chronicles_models.Chronicle.productIdentifier,
                "",
            ).label("title"),
        )
        .select_from(chronicles_models.Chronicle)
        .outerjoin(
            chronicles_models.ProductChronicle,
            chronicles_models.Chronicle.id == chronicles_models.ProductChronicle.chronicleId,
        )
        .outerjoin(offers_models.Product, chronicles_models.ProductChronicle.productId == offers_models.Product.id)
        .filter(chronicles_models.Chronicle.userId == user_id)
    ).all()

    for chronicle in chronicles:
        activity.append(serialization.ChronicleActivity(chronicle))

    activity = sorted(activity, key=lambda item: item.activityDate or datetime.datetime.min, reverse=True)

    return render_template(
        "accounts/get/details/activity.html",
        user_id=user_id,
        activity=activity,
    )


@public_accounts_blueprint.route("/<int:user_id>/gdpr-extract", methods=["POST"])
@utils.permission_required(perm_models.Permissions.EXTRACT_PUBLIC_ACCOUNT)
def create_extract_user_gdpr_data(user_id: int) -> utils.BackofficeResponse:
    user = (
        db.session.query(users_models.User)
        .filter(
            users_models.User.id == user_id,
        )
        .options(
            sa_orm.load_only(users_models.User.firstName, users_models.User.lastName, users_models.User.roles),
            sa_orm.joinedload(users_models.User.gdprUserDataExtracts),
        )
        .one_or_none()
    )
    if not user:
        raise NotFound()

    if not (user.is_beneficiary or user.roles == []):
        raise NotFound()

    if has_gdpr_extract(user=user):
        flash("Une extraction de données est déjà en cours pour cet utilisateur.", "warning")
        return redirect(url_for(".get_public_account", user_id=user_id))

    gdpr_data = users_models.GdprUserDataExtract(
        userId=user_id,
        authorUserId=current_user.id,
    )
    db.session.add(gdpr_data)
    db.session.flush()
    flash(
        Markup("L'extraction des données de l'utilisateur <b>{name}</b> a été demandée.").format(name=user.full_name),
        "success",
    )

    return redirect(url_for(".get_public_account", user_id=user_id))


def has_gdpr_extract(user: users_models.User) -> bool:
    if not user.gdprUserDataExtracts:
        return False
    return any(not extract.is_expired for extract in user.gdprUserDataExtracts)


@public_accounts_blueprint.route("/<int:user_id>/invalidate-password", methods=["POST"])
@utils.permission_required(perm_models.Permissions.MANAGE_PUBLIC_ACCOUNT)
def invalidate_public_account_password(user_id: int) -> utils.BackofficeResponse:
    user = db.session.query(users_models.User).filter(users_models.User.id == user_id).one_or_none()
    if not user:
        raise NotFound()
    if not (user.is_beneficiary or user.roles == []):
        flash("Seul le mot de passe d'un compte bénéficiaire ou grand public peut être invalidé", "warning")
        return redirect(get_public_account_link(user_id, active_tab="history"), code=303)

    users_api.update_user_password(user, random_password())

    history_api.add_action(history_models.ActionType.USER_PASSWORD_INVALIDATED, author=current_user, user=user)
    flash("Le mot de passe du compte a bien été invalidé", "success")
    return redirect(get_public_account_link(user_id, active_tab="history"), code=303)


@public_accounts_blueprint.route("/<int:user_id>/send-reset-password-email", methods=["POST"])
@utils.permission_required(perm_models.Permissions.MANAGE_PUBLIC_ACCOUNT)
def send_public_account_reset_password_email(user_id: int) -> utils.BackofficeResponse:
    user = db.session.query(users_models.User).filter(users_models.User.id == user_id).one_or_none()
    if not user:
        raise NotFound()
    if not (user.is_beneficiary or user.roles == []):
        flash("La fonctionnalité n'est disponible que pour un compte bénéficiaire ou grand public", "warning")
        return redirect(get_public_account_link(user_id, active_tab="history"), code=303)

    users_api.request_password_reset(user)

    flash("L'envoi du mail de changement de mot de passe a été initié", "success")
    return redirect(get_public_account_link(user_id, active_tab="history"), code=303)


def _render_individual_bookings(bookings_ids: list[int] | None = None) -> utils.BackofficeResponse:
    bookings: list[bookings_models.Booking] = []
    if bookings_ids:
        query = db.session.query(bookings_models.Booking).filter(
            bookings_models.Booking.id.in_(bookings_ids),
        )
        bookings = _apply_bookings_joined_loads(query).all()

    return render_template(
        "accounts/get/details/bookings_rows.html",
        bookings=bookings,
    )


@public_accounts_blueprint.route("/bookings/<int:booking_id>/mark-as-fraudulent", methods=["POST"])
@utils.permission_required(perm_models.Permissions.MANAGE_FRAUDULENT_BOOKING_INFO)
def mark_booking_as_fraudulent(booking_id: int) -> utils.BackofficeResponse:
    form = account_forms.TagFraudulentBookingsForm()
    if not form.validate():
        flash(utils.build_form_error_msg(form), "warning")
        return _render_individual_bookings()

    booking_helpers.tag_bookings_as_fraudulent(bookings_ids=[booking_id], send_emails=form.send_mails.data)

    return _render_individual_bookings([booking_id])


@public_accounts_blueprint.route("/bookings/<int:booking_id>/mark-as-not-fraudulent", methods=["POST"])
@utils.permission_required(perm_models.Permissions.MANAGE_FRAUDULENT_BOOKING_INFO)
def mark_booking_as_not_fraudulent(booking_id: int) -> utils.BackofficeResponse:
    form = empty_forms.EmptyForm()

    if not form.validate():
        flash(utils.build_form_error_msg(form), "warning")
        return _render_individual_bookings()

    db.session.query(bookings_models.FraudulentBookingTag).filter(
        bookings_models.FraudulentBookingTag.bookingId == booking_id
    ).delete(synchronize_session=False)
    db.session.flush()

    return _render_individual_bookings([booking_id])
