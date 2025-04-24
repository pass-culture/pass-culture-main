import datetime
import enum
from functools import partial
from operator import attrgetter
import re
from types import NotImplementedType
import typing

from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from flask_login import current_user
from markupsafe import Markup
import sqlalchemy as sa
import sqlalchemy.orm as sa_orm
from werkzeug.exceptions import BadRequest
from werkzeug.exceptions import NotFound

from pcapi import settings
from pcapi.core.bookings import models as bookings_models
from pcapi.core.external.attributes import api as external_attributes_api
from pcapi.core.finance import deposit_api
from pcapi.core.finance import exceptions as finance_exceptions
from pcapi.core.finance import models as finance_models
from pcapi.core.fraud import api as fraud_api
from pcapi.core.fraud import exceptions as fraud_exceptions
from pcapi.core.fraud import models as fraud_models
from pcapi.core.history import api as history_api
from pcapi.core.history import models as history_models
from pcapi.core.mails.transactional.users.personal_data_updated import send_beneficiary_personal_data_updated
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offers import models as offers_models
from pcapi.core.permissions import models as perm_models
from pcapi.core.subscription import api as subscription_api
from pcapi.core.subscription import exceptions as subscription_exceptions
from pcapi.core.subscription.models import SubscriptionItemStatus
from pcapi.core.subscription.models import SubscriptionStep
from pcapi.core.subscription.phone_validation import api as phone_validation_api
from pcapi.core.subscription.phone_validation import exceptions as phone_validation_exceptions
from pcapi.core.users import api as users_api
from pcapi.core.users import constants as users_constants
from pcapi.core.users import eligibility_api
from pcapi.core.users import exceptions as users_exceptions
from pcapi.core.users import models as users_models
from pcapi.core.users import utils as users_utils
from pcapi.core.users.email import update as email_update
from pcapi.domain.password import random_password
from pcapi.models import db
from pcapi.models.beneficiary_import import BeneficiaryImport
from pcapi.models.beneficiary_import_status import BeneficiaryImportStatus
from pcapi.models.feature import DisabledFeatureError
from pcapi.models.pc_object import BaseQuery
from pcapi.repository.session_management import atomic
from pcapi.repository.session_management import mark_transaction_as_invalid
from pcapi.routes.backoffice import search_utils
from pcapi.routes.backoffice import utils
from pcapi.routes.backoffice.forms import empty as empty_forms
from pcapi.routes.backoffice.users import forms as user_forms
from pcapi.utils import email as email_utils

from . import forms as account_forms
from . import serialization


public_accounts_blueprint = utils.child_backoffice_blueprint(
    "public_accounts",
    __name__,
    url_prefix="/public-accounts",
    permission=perm_models.Permissions.READ_PUBLIC_ACCOUNT,
)


def _load_suspension_info(query: BaseQuery) -> BaseQuery:
    # Partial joined load with ActionHistory avoids N+1 query to show suspension reason, but the number of fetched rows
    # would be greater than the number of results when a single user has several suspension actions.
    # So these expressions use a subquery so that result count is accurate, and the redirection well forced when a
    # single card would be displayed.
    return query.options(
        sa_orm.with_expression(
            users_models.User.suspension_reason_expression,
            users_models.User.suspension_reason.expression,  # type: ignore[attr-defined]
        ),
        sa_orm.with_expression(
            users_models.User.suspension_date_expression,
            users_models.User.suspension_date.expression,  # type: ignore[attr-defined]
        ),
    )


def _load_current_deposit_data(query: BaseQuery, join_needed: bool = True) -> BaseQuery:
    # partial joined load with Deposit and Recredit to avoid N+1, show the version of the current
    # deposit and not mess with the pagination as a beneficiary cannot have multiple deposits active
    # at the same time
    if join_needed:
        query = query.outerjoin(
            finance_models.Deposit,
            sa.and_(
                users_models.User.id == finance_models.Deposit.userId,
                finance_models.Deposit.expirationDate > datetime.datetime.utcnow(),
            ),
        )
    return query.options(sa_orm.contains_eager(users_models.User.deposits))


@public_accounts_blueprint.route("<int:user_id>/anonymize", methods=["POST"])
@utils.permission_required(perm_models.Permissions.ANONYMIZE_PUBLIC_ACCOUNT)
def anonymize_public_account(user_id: int) -> utils.BackofficeResponse:
    user = (
        db.session.query(users_models.User)
        .filter_by(id=user_id)
        .options(
            sa_orm.joinedload(users_models.User.deposits),
            sa_orm.joinedload(users_models.User.gdprUserDataExtract),
        )
        .one_or_none()
    )

    if not user:
        raise NotFound()

    form = empty_forms.EmptyForm()
    if not form.validate():
        flash(utils.build_form_error_msg(form), "warning")
        return redirect(url_for("backoffice_web.public_accounts.get_public_account", user_id=user_id), code=303)

    if users_api.has_unprocessed_extract(user):
        flash("Une extraction de données est en cours pour cet utilisateur.", "warning")
        return redirect(url_for(".get_public_account", user_id=user_id))

    if users_api.is_beneficiary_anonymizable(user):
        _anonymize_user(user, current_user)
    elif users_api.is_only_beneficiary(user):
        _pre_anonymize_user(user, current_user)
    else:
        raise BadRequest()

    return redirect(url_for(".get_public_account", user_id=user_id))


def _anonymize_user(user: users_models.User, author: users_models.User) -> None:
    user_anonymized = users_api.anonymize_user(user, author=current_user, force=True)
    if user_anonymized:
        db.session.flush()
        flash("Les informations de l'utilisateur ont été anonymisées", "success")
    else:
        mark_transaction_as_invalid()
        flash("Une erreur est survenue lors de l'anonymisation de l'utilisateur", "warning")


def _pre_anonymize_user(user: users_models.User, author: users_models.User) -> None:
    if users_api.is_suspended_for_less_than_five_years(user):
        db.session.add(users_models.GdprUserAnonymization(user=user))
        db.session.flush()
        flash(
            "L'utilisateur sera anonymisé quand il aura plus de 21 ans et 5 ans après sa suspension pour fraude",
            "success",
        )
    else:
        try:
            users_api.pre_anonymize_user(user, author, is_backoffice_action=True)
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
    if not form.validate():
        return render_search_template(form), 400

    users_query = users_api.search_public_account(form.q.data)
    users_query = search_utils.apply_filter_on_beneficiary_status(users_query, form.filter.data)
    users_query = _load_suspension_info(users_query)
    users_query = _load_current_deposit_data(users_query, join_needed=False)
    paginated_rows = users_query.paginate(page=form.page.data, per_page=form.per_page.data)

    # Do NOT call users.count() after search_public_account, this would make one more request on all users every time
    # (so it would select count twice: in users.count() and in users.paginate)
    if paginated_rows.total == 0 and email_utils.is_valid_email(email_utils.sanitize_email(form.q.data)):
        users_query = users_api.search_public_account_in_history_email(form.q.data)
        users_query = _load_suspension_info(users_query)
        users_query = _load_current_deposit_data(users_query)
        paginated_rows = users_query.paginate(page=form.page.data, per_page=form.per_page.data)

    if paginated_rows.total == 1:
        return redirect(
            url_for(
                ".get_public_account",
                user_id=paginated_rows.items[0].id,
                q=form.q.data,
                filter=form.filter.data,
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

    return render_template(
        "accounts/search.html",
        title="Recherche grand public",
        dst=url_for(".search_public_accounts"),
        form=form,
    )


def _convert_fraud_review_to_fraud_action_dict(fraud_review: fraud_models.BeneficiaryFraudReview) -> dict:
    return {
        "creationDate": fraud_review.dateReviewed,
        "type": "Revue manuelle",
        "applicableEligibilities": (
            [fraud_review.eligibilityType.value] if fraud_review.eligibilityType is not None else []
        ),
        "status": fraud_models.FraudReviewStatus(fraud_review.review).value,
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


def render_public_account_details(
    user_id: int,
    edit_account_form: account_forms.EditAccountForm | None = None,
) -> str:
    # Pre-load as many things as possible in the same request to avoid too many SQL queries
    # Note that extra queries are made in methods called by get_eligibility_history()
    # Do not joinedload bookings: combinations would cause too many rows returned by postgresql - fetched in a 2nd query
    user = (
        db.session.query(users_models.User)
        .filter_by(id=user_id)
        .options(
            sa_orm.joinedload(users_models.User.deposits).joinedload(finance_models.Deposit.recredits),
            sa_orm.subqueryload(users_models.User.userBookings).options(
                sa_orm.joinedload(bookings_models.Booking.stock).joinedload(offers_models.Stock.offer),
                sa_orm.joinedload(bookings_models.Booking.incidents).joinedload(
                    finance_models.BookingFinanceIncident.incident
                ),
                sa_orm.joinedload(bookings_models.Booking.offerer).load_only(offerers_models.Offerer.name),
                sa_orm.joinedload(bookings_models.Booking.venue)
                .load_only(offerers_models.Venue.bookingEmail)
                .joinedload(offerers_models.Venue.contact)
                .load_only(offerers_models.VenueContact.email),
                sa_orm.joinedload(bookings_models.Booking.fraudulentBookingTag),
            ),
            sa_orm.joinedload(users_models.User.beneficiaryFraudChecks),
            sa_orm.joinedload(users_models.User.beneficiaryFraudReviews),
            sa_orm.joinedload(users_models.User.beneficiaryImports)
            .joinedload(BeneficiaryImport.statuses)
            .joinedload(BeneficiaryImportStatus.author)
            .load_only(users_models.User.firstName, users_models.User.lastName),
            sa_orm.joinedload(users_models.User.action_history)
            .joinedload(history_models.ActionHistory.authorUser)
            .load_only(users_models.User.firstName, users_models.User.lastName),
            sa_orm.joinedload(users_models.User.email_history),
            sa_orm.joinedload(users_models.User.gdprUserDataExtract),
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
    history = get_public_account_history(user)
    duplicate_user_id = None
    eligibility_history = get_eligibility_history(user)
    user_current_eligibility = eligibility_api.get_eligibility_at_date(user.birth_date, datetime.datetime.utcnow())

    if user_current_eligibility is not None and user_current_eligibility.value in eligibility_history:
        subscription_items = [
            item
            for item in eligibility_history[user_current_eligibility.value].subscriptionItems
            if item.type == SubscriptionStep.IDENTITY_CHECK.value and item.status != SubscriptionItemStatus.OK.value
        ]

        if eligibility_history[user_current_eligibility.value].idCheckHistory and len(subscription_items) > 0:
            duplicate_user_id = _get_duplicate_fraud_history(eligibility_history)

    latest_fraud_check = _get_latest_fraud_check(
        eligibility_history, [fraud_models.FraudCheckType.UBBLE, fraud_models.FraudCheckType.DMS]
    )

    kwargs = {}

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

        kwargs.update(
            {
                "edit_account_form": edit_account_form,
                "edit_account_dst": url_for(".update_public_account", user_id=user.id),
                "manual_review_form": manual_review_form,
                "manual_review_dst": url_for(".review_public_account", user_id=user.id),
                "send_validation_code_form": empty_forms.EmptyForm(),
                "manual_phone_validation_form": empty_forms.EmptyForm(),
                "extract_user_form": extract_user_form,
            }
        )

        if not user.isEmailValidated:
            kwargs["resend_email_validation_form"] = empty_forms.EmptyForm()

    if (
        utils.has_current_user_permission(perm_models.Permissions.ANONYMIZE_PUBLIC_ACCOUNT)
        and not users_api.has_user_pending_anonymization(user_id)
        and users_models.UserRole.ANONYMIZED not in user.roles
    ):
        kwargs["anonymize_form"] = empty_forms.EmptyForm()
        kwargs["anonymize_public_accounts_dst"] = url_for(".anonymize_public_account", user_id=user.id)

    fraud_reviews_desc = _get_fraud_reviews_desc(user.beneficiaryFraudReviews)
    id_check_histories_desc = _get_id_check_histories_desc(eligibility_history)
    tunnel = _get_tunnel(user, eligibility_history, fraud_reviews_desc)
    fraud_actions = [_convert_fraud_review_to_fraud_action_dict(review) for review in user.beneficiaryFraudReviews] + [
        _convert_check_item_to_fraud_action_dict(idCheckHistory) for idCheckHistory in id_check_histories_desc
    ]
    fraud_actions_desc = sorted(
        fraud_actions,
        key=lambda action: action["creationDate"],
        reverse=True,
    )

    kwargs.update(user_forms.get_toggle_suspension_args(user, suspension_type=user_forms.SuspensionUserType.PUBLIC))
    return render_template(
        "accounts/get.html",
        search_form=account_forms.AccountSearchForm(),  # values taken from request
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
        **kwargs,
    )


def _get_fraud_reviews_desc(
    fraud_reviews: list[fraud_models.BeneficiaryFraudReview],
) -> list[fraud_models.BeneficiaryFraudReview]:
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
    id_checks_at_decree_start = [
        fraud_check
        for fraud_check in user.beneficiaryFraudChecks
        if fraud_check.status == fraud_models.FraudCheckStatus.OK
        and fraud_check.get_identity_check_birth_date() is not None
        and fraud_check.dateCreated < settings.CREDIT_V3_DECREE_DATETIME
    ]
    if not id_checks_at_decree_start:
        return None

    id_check_birth_date = max(f.get_identity_check_birth_date() for f in id_checks_at_decree_start)
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
        SubscriptionItemStatus.OK.value,
        SubscriptionItemStatus.NOT_APPLICABLE.value,
        SubscriptionItemStatus.NOT_ENABLED.value,
        SubscriptionItemStatus.SKIPPED.value,
    ):
        return RegistrationStepStatus.SUCCESS

    if status == SubscriptionItemStatus.KO.value:
        return RegistrationStepStatus.ERROR

    if status in (SubscriptionItemStatus.PENDING.value, SubscriptionItemStatus.SUSPICIOUS.value):
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
        fraud_actions_history: list[dict] | None = None,
        is_active: bool = False,
        is_disabled: bool = False,
        text: str = "",
    ):
        self.step_id = step_id
        self.description = description
        self.subscription_item_status = subscription_item_status
        self.icon = icon
        self.fraud_actions_history = list(fraud_actions_history or [])
        self.status = {
            "error": _get_status(subscription_item_status) == RegistrationStepStatus.ERROR,
            "success": _get_status(subscription_item_status) == RegistrationStepStatus.SUCCESS,
            "warning": _get_status(subscription_item_status) == RegistrationStepStatus.WARNING,
            "active": is_active,
            "disabled": is_disabled,
        }
        self.text = text

    def __repr__(self) -> str:
        fmt_status = " ".join([f"status[{key}]={value}" for key, value in self.status.items()])
        return (
            f"<RegistrationStep #{self.step_id} '{self.description}' "
            f"subscription_item_status={self.subscription_item_status} "
            f"icon=<{self.icon}> "
            f"fraud_actions_history={self.fraud_actions_history} "
            f"text='{self.text}' "
            f"{fmt_status}>"
        )

    def __eq__(self, other: object) -> bool | NotImplementedType:
        if not isinstance(other, RegistrationStep):
            raise NotImplementedError()
        return (
            self.fraud_actions_history == other.fraud_actions_history
            and self.step_id == other.step_id
            and self.description == other.description
            and self.subscription_item_status == other.subscription_item_status
            and self.icon == other.icon
            and self.status == other.status
            and self.text == other.text
        )


def _get_steps_for_tunnel(
    user: users_models.User,
    tunnel_type: TunnelType,
    subscription_item_status: dict,
    id_check_histories: list,
    fraud_reviews_desc: list[fraud_models.BeneficiaryFraudReview],
) -> list[RegistrationStep]:
    item_status_15_17 = subscription_item_status[users_models.EligibilityType.UNDERAGE.value]
    item_status_18 = subscription_item_status[users_models.EligibilityType.AGE18.value]
    item_status_17_18 = subscription_item_status[users_models.EligibilityType.AGE17_18.value]

    match tunnel_type:
        case TunnelType.AGE17:
            steps = _get_steps_tunnel_age17(user, id_check_histories, item_status_17_18, fraud_reviews_desc)
        case TunnelType.AGE18:
            steps = _get_steps_tunnel_age18(user, id_check_histories, item_status_17_18, fraud_reviews_desc)
        case TunnelType.AGE18_OLD:
            steps = _get_steps_tunnel_age18_old(user, id_check_histories, item_status_18, fraud_reviews_desc)
        case TunnelType.AGE17_18:
            steps = _get_steps_tunnel_age17_18(user, id_check_histories, item_status_17_18, fraud_reviews_desc)
        case TunnelType.UNDERAGE:
            steps = _get_steps_tunnel_underage(user, id_check_histories, item_status_15_17, fraud_reviews_desc)
        case TunnelType.UNDERAGE_AGE17:
            steps = _get_steps_tunnel_underage_age17(
                user, id_check_histories, item_status_15_17, item_status_17_18, fraud_reviews_desc
            )
        case TunnelType.UNDERAGE_AGE18_OLD:
            steps = _get_steps_tunnel_underage_age18_old(
                user, id_check_histories, item_status_15_17, item_status_18, fraud_reviews_desc
            )
        case TunnelType.UNDERAGE_AGE18:
            steps = _get_steps_tunnel_underage_age18(
                user, id_check_histories, item_status_15_17, item_status_17_18, fraud_reviews_desc
            )
        case TunnelType.UNDERAGE_AGE17_18:
            steps = _get_steps_tunnel_underage_age17_18(
                user, id_check_histories, item_status_15_17, item_status_17_18, fraud_reviews_desc
            )
        case _:
            steps = _get_steps_tunnel_unspecified(item_status_15_17, item_status_18, item_status_17_18)

    if tunnel_type == TunnelType.NOT_ELIGIBLE:
        return steps

    _set_steps_with_active_and_disabled(steps)
    return steps


def _set_steps_with_active_and_disabled(steps: list[RegistrationStep]) -> None:
    for step in reversed(steps):
        if step.subscription_item_status in [
            SubscriptionItemStatus.TODO.value,
            SubscriptionItemStatus.PENDING.value,
            SubscriptionItemStatus.OK.value,
            SubscriptionItemStatus.KO.value,
        ]:
            step.status["active"] = _get_status(step.subscription_item_status) is RegistrationStepStatus.SUCCESS
            break
        step.status["disabled"] = True


def _get_steps_tunnel_unspecified(
    item_status_15_17: dict, item_status_18: dict, item_status_17_18: dict
) -> list[RegistrationStep]:
    email_step_key = SubscriptionStep.EMAIL_VALIDATION.value
    email_status = (
        item_status_15_17.get(email_step_key)
        or item_status_18.get(email_step_key)
        or item_status_17_18.get(email_step_key)
        or SubscriptionItemStatus.PENDING.value
    )

    steps = [
        RegistrationStep(
            step_id=1,
            description=SubscriptionStep.EMAIL_VALIDATION.value,
            subscription_item_status=email_status,
            icon="bi-envelope-fill",
        ),
        RegistrationStep(
            step_id=2,
            description=TunnelType.NOT_ELIGIBLE.value,
            subscription_item_status=email_status,
            icon="bi-question-circle-fill",
            is_disabled=True,
        ),
    ]
    return steps


def _get_steps_tunnel_underage_age17(
    user: users_models.User,
    id_check_histories: list,
    item_status_15_17: dict,
    item_status_17_18: dict,
    fraud_reviews_desc: list[fraud_models.BeneficiaryFraudReview],
) -> list[RegistrationStep]:
    steps = [
        RegistrationStep(
            step_id=1,
            description=SubscriptionStep.EMAIL_VALIDATION.value,
            subscription_item_status=item_status_15_17[SubscriptionStep.EMAIL_VALIDATION.value],
            icon="bi-envelope-fill",
        ),
        RegistrationStep(
            step_id=2,
            description=SubscriptionStep.PROFILE_COMPLETION.value,
            subscription_item_status=item_status_15_17[SubscriptionStep.PROFILE_COMPLETION.value],
            icon="bi-house-check-fill",
            fraud_actions_history=[
                _convert_check_item_to_fraud_action_dict(id_check_history)
                for id_check_history in id_check_histories
                if id_check_history.type == fraud_models.FraudCheckType.PROFILE_COMPLETION.value
                and users_models.EligibilityType.UNDERAGE.value in id_check_history.applicable_eligibilities
            ],
        ),
        RegistrationStep(
            step_id=3,
            description=SubscriptionStep.IDENTITY_CHECK.value,
            subscription_item_status=item_status_15_17[SubscriptionStep.IDENTITY_CHECK.value],
            icon="bi-fingerprint",
            fraud_actions_history=[
                _convert_check_item_to_fraud_action_dict(id_check_history)
                for id_check_history in id_check_histories
                if id_check_history.type in {f.value for f in fraud_models.IDENTITY_CHECK_TYPES}
                and users_models.EligibilityType.UNDERAGE.value in id_check_history.applicable_eligibilities
            ],
        ),
        RegistrationStep(
            step_id=4,
            description=SubscriptionStep.HONOR_STATEMENT.value,
            subscription_item_status=item_status_15_17[SubscriptionStep.HONOR_STATEMENT.value],
            icon="bi-card-checklist",
        ),
        RegistrationStep(
            step_id=5,
            description=users_models.EligibilityType.UNDERAGE.value,
            subscription_item_status=(
                SubscriptionItemStatus.OK.value if user.received_pass_15_17 else SubscriptionItemStatus.VOID.value
            ),
            text="1517",
            fraud_actions_history=[
                _convert_fraud_review_to_fraud_action_dict(review)
                for review in fraud_reviews_desc
                if review.eligibilityType == users_models.EligibilityType.UNDERAGE
            ],
        ),
        RegistrationStep(
            step_id=6,
            description=SubscriptionStep.IDENTITY_CHECK.value,
            subscription_item_status=item_status_17_18[SubscriptionStep.IDENTITY_CHECK.value],
            icon="bi-fingerprint",
            fraud_actions_history=[
                _convert_check_item_to_fraud_action_dict(id_check_history)
                for id_check_history in id_check_histories
                if id_check_history.type in {f.value for f in fraud_models.IDENTITY_CHECK_TYPES}
                and users_models.EligibilityType.AGE17_18.value in id_check_history.applicable_eligibilities
            ],
        ),
        RegistrationStep(
            step_id=7,
            description=SubscriptionStep.HONOR_STATEMENT.value,
            subscription_item_status=item_status_17_18[SubscriptionStep.HONOR_STATEMENT.value],
            icon="bi-card-checklist",
        ),
        RegistrationStep(
            step_id=8,
            description="Pass 17",
            subscription_item_status=(
                SubscriptionItemStatus.OK.value if user.received_pass_17_18 else SubscriptionItemStatus.VOID.value
            ),
            text="17",
            fraud_actions_history=[
                _convert_fraud_review_to_fraud_action_dict(review)
                for review in fraud_reviews_desc
                if review.eligibilityType == users_models.EligibilityType.AGE17_18
            ],
        ),
    ]
    return steps


def _get_steps_tunnel_underage_age17_18(
    user: users_models.User,
    id_check_histories: list,
    item_status_15_17: dict,
    item_status_17_18: dict,
    fraud_reviews_desc: list[fraud_models.BeneficiaryFraudReview],
) -> list[RegistrationStep]:
    steps = [
        RegistrationStep(
            step_id=1,
            description=SubscriptionStep.EMAIL_VALIDATION.value,
            subscription_item_status=item_status_15_17[SubscriptionStep.EMAIL_VALIDATION.value],
            icon="bi-envelope-fill",
        ),
        RegistrationStep(
            step_id=2,
            description=SubscriptionStep.PROFILE_COMPLETION.value,
            subscription_item_status=item_status_15_17[SubscriptionStep.PROFILE_COMPLETION.value],
            icon="bi-house-check-fill",
            fraud_actions_history=[
                _convert_check_item_to_fraud_action_dict(id_check_history)
                for id_check_history in id_check_histories
                if id_check_history.type == fraud_models.FraudCheckType.PROFILE_COMPLETION.value
                and users_models.EligibilityType.UNDERAGE.value in id_check_history.applicable_eligibilities
            ],
        ),
        RegistrationStep(
            step_id=3,
            description=SubscriptionStep.IDENTITY_CHECK.value,
            subscription_item_status=item_status_15_17[SubscriptionStep.IDENTITY_CHECK.value],
            icon="bi-fingerprint",
            fraud_actions_history=[
                _convert_check_item_to_fraud_action_dict(id_check_history)
                for id_check_history in id_check_histories
                if id_check_history.type in {f.value for f in fraud_models.IDENTITY_CHECK_TYPES}
                and users_models.EligibilityType.UNDERAGE.value in id_check_history.applicable_eligibilities
            ],
        ),
        RegistrationStep(
            step_id=4,
            description=SubscriptionStep.HONOR_STATEMENT.value,
            subscription_item_status=item_status_15_17[SubscriptionStep.HONOR_STATEMENT.value],
            icon="bi-card-checklist",
        ),
        RegistrationStep(
            step_id=5,
            description=users_models.EligibilityType.UNDERAGE.value,
            subscription_item_status=(
                SubscriptionItemStatus.OK.value if user.received_pass_15_17 else SubscriptionItemStatus.VOID.value
            ),
            text="1517",
            fraud_actions_history=[
                _convert_fraud_review_to_fraud_action_dict(review)
                for review in fraud_reviews_desc
                if review.eligibilityType == users_models.EligibilityType.UNDERAGE
            ],
        ),
        RegistrationStep(
            step_id=6,
            description="age-17",
            subscription_item_status=(
                SubscriptionItemStatus.OK.value if user.received_pass_17_18 else SubscriptionItemStatus.VOID.value
            ),
            icon="bi-card-checklist",
            fraud_actions_history=[
                _convert_fraud_review_to_fraud_action_dict(review)
                for review in fraud_reviews_desc
                if review.eligibilityType == users_models.EligibilityType.AGE18
            ],
        ),
        RegistrationStep(
            step_id=7,
            description=SubscriptionStep.PHONE_VALIDATION.value,
            subscription_item_status=item_status_17_18[SubscriptionStep.PHONE_VALIDATION.value],
            icon="bi-telephone-fill",
            fraud_actions_history=[
                _convert_check_item_to_fraud_action_dict(id_check_history)
                for id_check_history in id_check_histories
                if id_check_history.type == fraud_models.FraudCheckType.PHONE_VALIDATION.value
                and users_models.EligibilityType.AGE18.value in id_check_history.applicable_eligibilities
            ],
        ),
        RegistrationStep(
            step_id=8,
            description=SubscriptionStep.PROFILE_COMPLETION.value,
            subscription_item_status=item_status_17_18[SubscriptionStep.PROFILE_COMPLETION.value],
            icon="bi-house-check-fill",
        ),
        RegistrationStep(
            step_id=9,
            description=SubscriptionStep.IDENTITY_CHECK.value,
            subscription_item_status=item_status_17_18[SubscriptionStep.IDENTITY_CHECK.value],
            icon="bi-fingerprint",
            fraud_actions_history=[
                _convert_check_item_to_fraud_action_dict(id_check_history)
                for id_check_history in id_check_histories
                if id_check_history.type in {f.value for f in fraud_models.IDENTITY_CHECK_TYPES}
                and users_models.EligibilityType.AGE18.value in id_check_history.applicable_eligibilities
            ],
        ),
        RegistrationStep(
            step_id=10,
            description=SubscriptionStep.HONOR_STATEMENT.value,
            subscription_item_status=item_status_17_18[SubscriptionStep.HONOR_STATEMENT.value],
            icon="bi-card-checklist",
        ),
        RegistrationStep(
            step_id=11,
            description="age-18",
            subscription_item_status=(
                SubscriptionItemStatus.OK.value if user.received_pass_18_v3 else SubscriptionItemStatus.VOID.value
            ),
            icon="bi-card-checklist",
            fraud_actions_history=[
                _convert_fraud_review_to_fraud_action_dict(review)
                for review in fraud_reviews_desc
                if review.eligibilityType == users_models.EligibilityType.AGE18
            ],
        ),
    ]
    return steps


def _get_steps_tunnel_underage_age18(
    user: users_models.User,
    id_check_histories: list,
    item_status_15_17: dict,
    item_status_17_18: dict,
    fraud_reviews_desc: list[fraud_models.BeneficiaryFraudReview],
) -> list[RegistrationStep]:
    steps = [
        RegistrationStep(
            step_id=1,
            description=SubscriptionStep.EMAIL_VALIDATION.value,
            subscription_item_status=item_status_15_17[SubscriptionStep.EMAIL_VALIDATION.value],
            icon="bi-envelope-fill",
        ),
        RegistrationStep(
            step_id=2,
            description=SubscriptionStep.PROFILE_COMPLETION.value,
            subscription_item_status=item_status_15_17[SubscriptionStep.PROFILE_COMPLETION.value],
            icon="bi-house-check-fill",
            fraud_actions_history=[
                _convert_check_item_to_fraud_action_dict(id_check_history)
                for id_check_history in id_check_histories
                if id_check_history.type == fraud_models.FraudCheckType.PROFILE_COMPLETION.value
                and users_models.EligibilityType.UNDERAGE.value in id_check_history.applicable_eligibilities
            ],
        ),
        RegistrationStep(
            step_id=3,
            description=SubscriptionStep.IDENTITY_CHECK.value,
            subscription_item_status=item_status_15_17[SubscriptionStep.IDENTITY_CHECK.value],
            icon="bi-fingerprint",
            fraud_actions_history=[
                _convert_check_item_to_fraud_action_dict(id_check_history)
                for id_check_history in id_check_histories
                if id_check_history.type in {f.value for f in fraud_models.IDENTITY_CHECK_TYPES}
                and users_models.EligibilityType.UNDERAGE.value in id_check_history.applicable_eligibilities
            ],
        ),
        RegistrationStep(
            step_id=4,
            description=SubscriptionStep.HONOR_STATEMENT.value,
            subscription_item_status=item_status_15_17[SubscriptionStep.HONOR_STATEMENT.value],
            icon="bi-card-checklist",
        ),
        RegistrationStep(
            step_id=5,
            description=users_models.EligibilityType.UNDERAGE.value,
            subscription_item_status=(
                SubscriptionItemStatus.OK.value if user.received_pass_15_17 else SubscriptionItemStatus.VOID.value
            ),
            text="1517",
            fraud_actions_history=[
                _convert_fraud_review_to_fraud_action_dict(review)
                for review in fraud_reviews_desc
                if review.eligibilityType == users_models.EligibilityType.UNDERAGE
            ],
        ),
        RegistrationStep(
            step_id=6,
            description=SubscriptionStep.PHONE_VALIDATION.value,
            subscription_item_status=item_status_17_18[SubscriptionStep.PHONE_VALIDATION.value],
            icon="bi-telephone-fill",
            fraud_actions_history=[
                _convert_check_item_to_fraud_action_dict(id_check_history)
                for id_check_history in id_check_histories
                if id_check_history.type == fraud_models.FraudCheckType.PHONE_VALIDATION.value
                and users_models.EligibilityType.AGE18.value in id_check_history.applicable_eligibilities
            ],
        ),
        RegistrationStep(
            step_id=7,
            description=SubscriptionStep.PROFILE_COMPLETION.value,
            subscription_item_status=item_status_17_18[SubscriptionStep.PROFILE_COMPLETION.value],
            icon="bi-house-check-fill",
        ),
        RegistrationStep(
            step_id=8,
            description=SubscriptionStep.IDENTITY_CHECK.value,
            subscription_item_status=item_status_17_18[SubscriptionStep.IDENTITY_CHECK.value],
            icon="bi-fingerprint",
            fraud_actions_history=[
                _convert_check_item_to_fraud_action_dict(id_check_history)
                for id_check_history in id_check_histories
                if id_check_history.type in {f.value for f in fraud_models.IDENTITY_CHECK_TYPES}
                and users_models.EligibilityType.AGE18.value in id_check_history.applicable_eligibilities
            ],
        ),
        RegistrationStep(
            step_id=9,
            description=SubscriptionStep.HONOR_STATEMENT.value,
            subscription_item_status=item_status_17_18[SubscriptionStep.HONOR_STATEMENT.value],
            icon="bi-card-checklist",
        ),
        RegistrationStep(
            step_id=10,
            description="age-18",
            subscription_item_status=(
                SubscriptionItemStatus.OK.value if user.received_pass_18_v3 else SubscriptionItemStatus.VOID.value
            ),
            icon="bi-card-checklist",
            fraud_actions_history=[
                _convert_fraud_review_to_fraud_action_dict(review)
                for review in fraud_reviews_desc
                if review.eligibilityType == users_models.EligibilityType.AGE18
            ],
        ),
    ]
    return steps


def _get_steps_tunnel_underage_age18_old(
    user: users_models.User,
    id_check_histories: list,
    item_status_15_17: dict,
    item_status_18: dict,
    fraud_reviews_desc: list[fraud_models.BeneficiaryFraudReview],
) -> list[RegistrationStep]:
    steps = [
        RegistrationStep(
            step_id=1,
            description=SubscriptionStep.EMAIL_VALIDATION.value,
            subscription_item_status=item_status_15_17[SubscriptionStep.EMAIL_VALIDATION.value],
            icon="bi-envelope-fill",
        ),
        RegistrationStep(
            step_id=2,
            description=SubscriptionStep.PROFILE_COMPLETION.value,
            subscription_item_status=item_status_15_17[SubscriptionStep.PROFILE_COMPLETION.value],
            icon="bi-house-check-fill",
            fraud_actions_history=[
                _convert_check_item_to_fraud_action_dict(id_check_history)
                for id_check_history in id_check_histories
                if id_check_history.type == fraud_models.FraudCheckType.PROFILE_COMPLETION.value
                and users_models.EligibilityType.UNDERAGE.value in id_check_history.applicable_eligibilities
            ],
        ),
        RegistrationStep(
            step_id=3,
            description=SubscriptionStep.IDENTITY_CHECK.value,
            subscription_item_status=item_status_15_17[SubscriptionStep.IDENTITY_CHECK.value],
            icon="bi-fingerprint",
            fraud_actions_history=[
                _convert_check_item_to_fraud_action_dict(id_check_history)
                for id_check_history in id_check_histories
                if id_check_history.type in {f.value for f in fraud_models.IDENTITY_CHECK_TYPES}
                and users_models.EligibilityType.UNDERAGE.value in id_check_history.applicable_eligibilities
            ],
        ),
        RegistrationStep(
            step_id=4,
            description=SubscriptionStep.HONOR_STATEMENT.value,
            subscription_item_status=item_status_15_17[SubscriptionStep.HONOR_STATEMENT.value],
            icon="bi-card-checklist",
        ),
        RegistrationStep(
            step_id=5,
            description=users_models.EligibilityType.UNDERAGE.value,
            subscription_item_status=(
                SubscriptionItemStatus.OK.value if user.received_pass_15_17 else SubscriptionItemStatus.VOID.value
            ),
            text="1517",
            fraud_actions_history=[
                _convert_fraud_review_to_fraud_action_dict(review)
                for review in fraud_reviews_desc
                if review.eligibilityType == users_models.EligibilityType.UNDERAGE
            ],
        ),
        RegistrationStep(
            step_id=6,
            description=SubscriptionStep.PHONE_VALIDATION.value,
            subscription_item_status=item_status_18[SubscriptionStep.PHONE_VALIDATION.value],
            icon="bi-telephone-fill",
            fraud_actions_history=[
                _convert_check_item_to_fraud_action_dict(id_check_history)
                for id_check_history in id_check_histories
                if id_check_history.type == fraud_models.FraudCheckType.PHONE_VALIDATION.value
                and users_models.EligibilityType.AGE18.value in id_check_history.applicable_eligibilities
            ],
        ),
        RegistrationStep(
            step_id=7,
            description=SubscriptionStep.PROFILE_COMPLETION.value,
            subscription_item_status=item_status_18[SubscriptionStep.PROFILE_COMPLETION.value],
            icon="bi-house-check-fill",
        ),
        RegistrationStep(
            step_id=8,
            description=SubscriptionStep.IDENTITY_CHECK.value,
            subscription_item_status=item_status_18[SubscriptionStep.IDENTITY_CHECK.value],
            icon="bi-fingerprint",
            fraud_actions_history=[
                _convert_check_item_to_fraud_action_dict(id_check_history)
                for id_check_history in id_check_histories
                if id_check_history.type in {f.value for f in fraud_models.IDENTITY_CHECK_TYPES}
                and users_models.EligibilityType.AGE18.value in id_check_history.applicable_eligibilities
            ],
        ),
        RegistrationStep(
            step_id=9,
            description=SubscriptionStep.HONOR_STATEMENT.value,
            subscription_item_status=item_status_18[SubscriptionStep.HONOR_STATEMENT.value],
            icon="bi-card-checklist",
        ),
        RegistrationStep(
            step_id=10,
            description="Ancien Pass 18",
            subscription_item_status=(
                SubscriptionItemStatus.OK.value if user.received_pass_18 else SubscriptionItemStatus.VOID.value
            ),
            icon="bi-card-checklist",
            fraud_actions_history=[
                _convert_fraud_review_to_fraud_action_dict(review)
                for review in fraud_reviews_desc
                if review.eligibilityType == users_models.EligibilityType.AGE18
            ],
        ),
    ]
    return steps


def _get_steps_tunnel_age17(
    user: users_models.User,
    id_check_histories: list,
    item_status_17_18: dict,
    fraud_reviews_desc: list[fraud_models.BeneficiaryFraudReview],
) -> list[RegistrationStep]:
    steps = [
        RegistrationStep(
            step_id=1,
            description=SubscriptionStep.EMAIL_VALIDATION.value,
            subscription_item_status=item_status_17_18[SubscriptionStep.EMAIL_VALIDATION.value],
            icon="bi-envelope-fill",
        ),
        RegistrationStep(
            step_id=2,
            description=SubscriptionStep.PROFILE_COMPLETION.value,
            subscription_item_status=item_status_17_18[SubscriptionStep.PROFILE_COMPLETION.value],
            icon="bi-house-check-fill",
            fraud_actions_history=[
                _convert_check_item_to_fraud_action_dict(id_check_history)
                for id_check_history in id_check_histories
                if id_check_history.type == fraud_models.FraudCheckType.PROFILE_COMPLETION.value
                and users_models.EligibilityType.AGE17_18.value in id_check_history.applicable_eligibilities
            ],
        ),
        RegistrationStep(
            step_id=3,
            description=SubscriptionStep.IDENTITY_CHECK.value,
            subscription_item_status=item_status_17_18[SubscriptionStep.IDENTITY_CHECK.value],
            icon="bi-fingerprint",
            fraud_actions_history=[
                _convert_check_item_to_fraud_action_dict(id_check_history)
                for id_check_history in id_check_histories
                if id_check_history.type in {f.value for f in fraud_models.IDENTITY_CHECK_TYPES}
                and users_models.EligibilityType.AGE17_18.value in id_check_history.applicable_eligibilities
            ],
        ),
        RegistrationStep(
            step_id=4,
            description=SubscriptionStep.HONOR_STATEMENT.value,
            subscription_item_status=item_status_17_18[SubscriptionStep.HONOR_STATEMENT.value],
            icon="bi-card-checklist",
        ),
        RegistrationStep(
            step_id=5,
            description="Pass 17",
            subscription_item_status=(
                SubscriptionItemStatus.OK.value if user.received_pass_17_18 else SubscriptionItemStatus.VOID.value
            ),
            fraud_actions_history=[
                _convert_fraud_review_to_fraud_action_dict(review)
                for review in fraud_reviews_desc
                if review.eligibilityType == users_models.EligibilityType.AGE17_18
            ],
        ),
    ]
    return steps


def _get_steps_tunnel_age17_18(
    user: users_models.User,
    id_check_histories: list,
    item_status_17_18: dict,
    fraud_reviews_desc: list[fraud_models.BeneficiaryFraudReview],
) -> list[RegistrationStep]:
    steps = [
        RegistrationStep(
            step_id=1,
            description=SubscriptionStep.EMAIL_VALIDATION.value,
            subscription_item_status=item_status_17_18[SubscriptionStep.EMAIL_VALIDATION.value],
            icon="bi-envelope-fill",
        ),
        RegistrationStep(
            step_id=2,
            description=SubscriptionStep.PROFILE_COMPLETION.value,
            subscription_item_status=item_status_17_18[SubscriptionStep.PROFILE_COMPLETION.value],
            icon="bi-house-check-fill",
            fraud_actions_history=[
                _convert_check_item_to_fraud_action_dict(id_check_history)
                for id_check_history in id_check_histories
                if id_check_history.type == fraud_models.FraudCheckType.PROFILE_COMPLETION.value
                and users_models.EligibilityType.AGE17_18.value in id_check_history.applicable_eligibilities
            ],
        ),
        RegistrationStep(
            step_id=3,
            description=SubscriptionStep.IDENTITY_CHECK.value,
            subscription_item_status=item_status_17_18[SubscriptionStep.IDENTITY_CHECK.value],
            icon="bi-fingerprint",
            fraud_actions_history=[
                _convert_check_item_to_fraud_action_dict(id_check_history)
                for id_check_history in id_check_histories
                if id_check_history.type in {f.value for f in fraud_models.IDENTITY_CHECK_TYPES}
                and users_models.EligibilityType.AGE17_18.value in id_check_history.applicable_eligibilities
            ],
        ),
        RegistrationStep(
            step_id=4,
            description=SubscriptionStep.HONOR_STATEMENT.value,
            subscription_item_status=item_status_17_18[SubscriptionStep.HONOR_STATEMENT.value],
            icon="bi-card-checklist",
        ),
        RegistrationStep(
            step_id=5,
            description="Pass 17",
            subscription_item_status=(
                SubscriptionItemStatus.OK.value if user.received_pass_17_18 else SubscriptionItemStatus.VOID.value
            ),
            text="17",
            fraud_actions_history=[
                _convert_fraud_review_to_fraud_action_dict(review)
                for review in fraud_reviews_desc
                if review.eligibilityType == users_models.EligibilityType.AGE17_18
            ],
        ),
        RegistrationStep(
            step_id=6,
            description=SubscriptionStep.PHONE_VALIDATION.value,
            subscription_item_status=item_status_17_18[SubscriptionStep.PHONE_VALIDATION.value],
            icon="bi-telephone-fill",
            fraud_actions_history=[
                _convert_check_item_to_fraud_action_dict(id_check_history)
                for id_check_history in id_check_histories
                if id_check_history.type == fraud_models.FraudCheckType.PHONE_VALIDATION.value
                and users_models.EligibilityType.AGE17_18.value in id_check_history.applicable_eligibilities
            ],
        ),
        RegistrationStep(
            step_id=7,
            description=SubscriptionStep.PROFILE_COMPLETION.value,
            subscription_item_status=item_status_17_18[SubscriptionStep.PROFILE_COMPLETION.value],
            icon="bi-house-check-fill",
            fraud_actions_history=[
                _convert_check_item_to_fraud_action_dict(id_check_history)
                for id_check_history in id_check_histories
                if id_check_history.type == fraud_models.FraudCheckType.PROFILE_COMPLETION.value
                and users_models.EligibilityType.AGE17_18.value in id_check_history.applicable_eligibilities
            ],
        ),
        RegistrationStep(
            step_id=8,
            description=SubscriptionStep.IDENTITY_CHECK.value,
            subscription_item_status=item_status_17_18[SubscriptionStep.IDENTITY_CHECK.value],
            icon="bi-fingerprint",
            fraud_actions_history=[
                _convert_check_item_to_fraud_action_dict(id_check_history)
                for id_check_history in id_check_histories
                if id_check_history.type in {f.value for f in fraud_models.IDENTITY_CHECK_TYPES}
                and users_models.EligibilityType.AGE17_18.value in id_check_history.applicable_eligibilities
            ],
        ),
        RegistrationStep(
            step_id=9,
            description=SubscriptionStep.HONOR_STATEMENT.value,
            subscription_item_status=item_status_17_18[SubscriptionStep.HONOR_STATEMENT.value],
            icon="bi-card-checklist",
        ),
        RegistrationStep(
            step_id=10,
            description="Pass 18",
            subscription_item_status=(
                SubscriptionItemStatus.OK.value if user.received_pass_18_v3 else SubscriptionItemStatus.VOID.value
            ),
            text="18",
        ),
    ]
    return steps


def _get_steps_tunnel_age18(
    user: users_models.User,
    id_check_histories: list,
    item_status_17_18: dict,
    fraud_reviews_desc: list[fraud_models.BeneficiaryFraudReview],
) -> list[RegistrationStep]:
    steps = [
        RegistrationStep(
            step_id=1,
            description=SubscriptionStep.EMAIL_VALIDATION.value,
            subscription_item_status=item_status_17_18[SubscriptionStep.EMAIL_VALIDATION.value],
            icon="bi-envelope-fill",
        ),
        RegistrationStep(
            step_id=2,
            description=SubscriptionStep.PHONE_VALIDATION.value,
            subscription_item_status=item_status_17_18[SubscriptionStep.PHONE_VALIDATION.value],
            icon="bi-telephone-fill",
            fraud_actions_history=[
                _convert_check_item_to_fraud_action_dict(id_check_history)
                for id_check_history in id_check_histories
                if id_check_history.type == fraud_models.FraudCheckType.PHONE_VALIDATION.value
                and users_models.EligibilityType.AGE17_18.value in id_check_history.applicable_eligibilities
            ],
        ),
        RegistrationStep(
            step_id=3,
            description=SubscriptionStep.PROFILE_COMPLETION.value,
            subscription_item_status=item_status_17_18[SubscriptionStep.PROFILE_COMPLETION.value],
            icon="bi-house-check-fill",
            fraud_actions_history=[
                _convert_check_item_to_fraud_action_dict(id_check_history)
                for id_check_history in id_check_histories
                if id_check_history.type == fraud_models.FraudCheckType.PROFILE_COMPLETION.value
                and users_models.EligibilityType.AGE17_18.value in id_check_history.applicable_eligibilities
            ],
        ),
        RegistrationStep(
            step_id=4,
            description=SubscriptionStep.IDENTITY_CHECK.value,
            subscription_item_status=item_status_17_18[SubscriptionStep.IDENTITY_CHECK.value],
            icon="bi-fingerprint",
            fraud_actions_history=[
                _convert_check_item_to_fraud_action_dict(id_check_history)
                for id_check_history in id_check_histories
                if id_check_history.type in {f.value for f in fraud_models.IDENTITY_CHECK_TYPES}
                and users_models.EligibilityType.AGE17_18.value in id_check_history.applicable_eligibilities
            ],
        ),
        RegistrationStep(
            step_id=5,
            description=SubscriptionStep.HONOR_STATEMENT.value,
            subscription_item_status=item_status_17_18[SubscriptionStep.HONOR_STATEMENT.value],
            icon="bi-card-checklist",
        ),
        RegistrationStep(
            step_id=6,
            description="Pass 18",
            subscription_item_status=(
                SubscriptionItemStatus.OK.value if user.received_pass_18_v3 else SubscriptionItemStatus.VOID.value
            ),
            text="18",
            fraud_actions_history=[
                _convert_fraud_review_to_fraud_action_dict(review)
                for review in fraud_reviews_desc
                if review.eligibilityType == users_models.EligibilityType.AGE17_18
            ],
        ),
    ]
    return steps


def _get_steps_tunnel_age18_old(
    user: users_models.User,
    id_check_histories: list,
    item_status_18: dict,
    fraud_reviews_desc: list[fraud_models.BeneficiaryFraudReview],
) -> list[RegistrationStep]:
    steps = [
        RegistrationStep(
            step_id=1,
            description=SubscriptionStep.EMAIL_VALIDATION.value,
            subscription_item_status=item_status_18[SubscriptionStep.EMAIL_VALIDATION.value],
            icon="bi-envelope-fill",
        ),
        RegistrationStep(
            step_id=2,
            description=SubscriptionStep.PHONE_VALIDATION.value,
            subscription_item_status=item_status_18[SubscriptionStep.PHONE_VALIDATION.value],
            icon="bi-telephone-fill",
            fraud_actions_history=[
                _convert_check_item_to_fraud_action_dict(id_check_history)
                for id_check_history in id_check_histories
                if id_check_history.type == fraud_models.FraudCheckType.PHONE_VALIDATION.value
                and users_models.EligibilityType.AGE18.value in id_check_history.applicable_eligibilities
            ],
        ),
        RegistrationStep(
            step_id=3,
            description=SubscriptionStep.PROFILE_COMPLETION.value,
            subscription_item_status=item_status_18[SubscriptionStep.PROFILE_COMPLETION.value],
            icon="bi-house-check-fill",
            fraud_actions_history=[
                _convert_check_item_to_fraud_action_dict(id_check_history)
                for id_check_history in id_check_histories
                if id_check_history.type == fraud_models.FraudCheckType.PROFILE_COMPLETION.value
                and users_models.EligibilityType.AGE18.value in id_check_history.applicable_eligibilities
            ],
        ),
        RegistrationStep(
            step_id=4,
            description=SubscriptionStep.IDENTITY_CHECK.value,
            subscription_item_status=item_status_18[SubscriptionStep.IDENTITY_CHECK.value],
            icon="bi-fingerprint",
            fraud_actions_history=[
                _convert_check_item_to_fraud_action_dict(id_check_history)
                for id_check_history in id_check_histories
                if id_check_history.type in {f.value for f in fraud_models.IDENTITY_CHECK_TYPES}
                and users_models.EligibilityType.AGE18.value in id_check_history.applicable_eligibilities
            ],
        ),
        RegistrationStep(
            step_id=5,
            description=SubscriptionStep.HONOR_STATEMENT.value,
            subscription_item_status=item_status_18[SubscriptionStep.HONOR_STATEMENT.value],
            icon="bi-card-checklist",
        ),
        RegistrationStep(
            step_id=6,
            description="Ancien Pass 18",
            subscription_item_status=(
                SubscriptionItemStatus.OK.value if user.received_pass_18 else SubscriptionItemStatus.VOID.value
            ),
            text="18",
            fraud_actions_history=[
                _convert_fraud_review_to_fraud_action_dict(review)
                for review in fraud_reviews_desc
                if review.eligibilityType == users_models.EligibilityType.AGE18
            ],
        ),
    ]
    return steps


def _get_steps_tunnel_underage(
    user: users_models.User,
    id_check_histories: list,
    item_status_15_17: dict,
    fraud_reviews_desc: list[fraud_models.BeneficiaryFraudReview],
) -> list[RegistrationStep]:
    steps = [
        RegistrationStep(
            step_id=1,
            description=SubscriptionStep.EMAIL_VALIDATION.value,
            subscription_item_status=item_status_15_17[SubscriptionStep.EMAIL_VALIDATION.value],
            icon="bi-envelope-fill",
        ),
        RegistrationStep(
            step_id=2,
            description=SubscriptionStep.PROFILE_COMPLETION.value,
            subscription_item_status=item_status_15_17[SubscriptionStep.PROFILE_COMPLETION.value],
            icon="bi-house-check-fill",
            fraud_actions_history=[
                _convert_check_item_to_fraud_action_dict(id_check_history)
                for id_check_history in id_check_histories
                if id_check_history.type == fraud_models.FraudCheckType.PROFILE_COMPLETION.value
                and users_models.EligibilityType.UNDERAGE.value in id_check_history.applicable_eligibilities
            ],
        ),
        RegistrationStep(
            step_id=3,
            description=SubscriptionStep.IDENTITY_CHECK.value,
            subscription_item_status=item_status_15_17[SubscriptionStep.IDENTITY_CHECK.value],
            icon="bi-fingerprint",
            fraud_actions_history=[
                _convert_check_item_to_fraud_action_dict(id_check_history)
                for id_check_history in id_check_histories
                if id_check_history.type in {f.value for f in fraud_models.IDENTITY_CHECK_TYPES}
                and users_models.EligibilityType.UNDERAGE.value in id_check_history.applicable_eligibilities
            ],
        ),
        RegistrationStep(
            step_id=4,
            description=SubscriptionStep.HONOR_STATEMENT.value,
            subscription_item_status=item_status_15_17[SubscriptionStep.HONOR_STATEMENT.value],
            icon="bi-card-checklist",
        ),
        RegistrationStep(
            step_id=5,
            description="Ancien Pass 15-17",
            subscription_item_status=(
                SubscriptionItemStatus.OK.value if user.received_pass_15_17 else SubscriptionItemStatus.VOID.value
            ),
            text="1517",
            fraud_actions_history=[
                _convert_fraud_review_to_fraud_action_dict(review)
                for review in fraud_reviews_desc
                if review.eligibilityType == users_models.EligibilityType.UNDERAGE
            ],
        ),
    ]
    return steps


def _get_tunnel(
    user: users_models.User,
    eligibility_history: dict[str, serialization.EligibilitySubscriptionHistoryModel],
    fraud_reviews_desc: list[fraud_models.BeneficiaryFraudReview],
) -> dict:
    subscription_item_status = _get_subscription_item_status_by_eligibility(eligibility_history)
    tunnel_type = _get_tunnel_type(user)
    id_check_histories = _get_id_check_histories_desc(eligibility_history)
    steps = _get_steps_for_tunnel(user, tunnel_type, subscription_item_status, id_check_histories, fraud_reviews_desc)
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
                    "Le numéro de pièce d'identité <b>{id_piece_number}</b> est déja associé à un autre compte utilisateur."
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
    except subscription_exceptions.SubscriptionException as exc:
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
    if form.status.data == fraud_models.FraudReviewStatus.OK.value:
        if user.has_beneficiary_role and eligibility == users_models.EligibilityType.UNDERAGE:
            flash(
                "Le compte est déjà bénéficiaire (18+) il ne peut pas aussi être bénéficiaire (15-17)",
                "warning",
            )
            return redirect(get_public_account_link(user_id), code=303)

        has_grant_17_18_deposit = (
            user.deposit is not None and user.deposit.type == finance_models.DepositType.GRANT_17_18
        )
        if has_grant_17_18_deposit and eligibility == users_models.EligibilityType.AGE18:
            flash(
                "Le compte est déjà bénéficiaire du Pass 17-18, il ne peut pas aussi être bénéficiaire de l'ancien Pass 18",
                "warning",
            )
            return redirect(get_public_account_link(user_id), code=303)

    try:
        if eligibility == users_models.EligibilityType.AGE18 and user.has_underage_beneficiary_role:
            deposit_api.expire_current_deposit_for_user(user=user)
        fraud_api.validate_beneficiary(
            user=user,
            reviewer=current_user,
            reason=form.reason.data,
            review=fraud_models.FraudReviewStatus(form.status.data),
            reviewed_eligibility=eligibility,
        )
    except (fraud_exceptions.FraudException, finance_exceptions.FinanceException, DisabledFeatureError) as exc:
        mark_transaction_as_invalid()
        flash(
            Markup("Une erreur s'est produite : {message}").format(message=str(exc) or exc.__class__.__name__),
            "warning",
        )
    else:
        flash("Validation réussie", "success")

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
                serialization.IdCheckItemModel.from_orm(fraud_check)
                for fraud_check in user.beneficiaryFraudChecks
                if serialization.get_fraud_check_eligibility_type(fraud_check) == eligibility
            ],
        )

    return subscriptions


def _get_latest_fraud_check(
    eligibility_history: dict[str, serialization.EligibilitySubscriptionHistoryModel],
    check_types: list[fraud_models.FraudCheckType],
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
        fraud_models.FraudReasonCode.DUPLICATE_USER.value,
        fraud_models.FraudReasonCode.DUPLICATE_ID_PIECE_NUMBER.value,
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
    user: users_models.User,
) -> list[serialization.AccountAction | history_models.ActionHistory]:
    # All data should have been joinloaded with user
    history: list[history_models.ActionHistory | serialization.AccountAction] = list(user.action_history)

    if history_models.ActionType.USER_CREATED not in (action.actionType for action in user.action_history):
        history.append(serialization.AccountCreatedAction(user))

    for change in user.email_history:
        history.append(serialization.EmailChangeAction(change))

    for fraud_check in user.beneficiaryFraudChecks:
        history.append(serialization.FraudCheckAction(fraud_check))

    for review in user.beneficiaryFraudReviews:
        history.append(serialization.ReviewAction(review))

    for import_ in user.beneficiaryImports:
        for status in import_.statuses:
            history.append(serialization.ImportStatusAction(import_, status))

    for deposit in user.deposits:
        history.append(serialization.DepositAction(deposit))
        for recredit in deposit.recredits:
            history.append(serialization.RecreditAction(recredit))

    history = sorted(history, key=lambda item: item.actionDate or datetime.datetime.min, reverse=True)

    return history


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
            sa_orm.joinedload(users_models.User.gdprUserDataExtract),
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
    if not user.gdprUserDataExtract:
        return False
    return any(not extract.is_expired for extract in user.gdprUserDataExtract)


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
