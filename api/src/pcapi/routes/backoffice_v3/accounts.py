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
from flask_sqlalchemy import Pagination
import pydantic
import sqlalchemy as sa
from werkzeug.exceptions import NotFound

from pcapi.core.bookings import models as bookings_models
from pcapi.core.external.attributes import api as external_attributes_api
import pcapi.core.fraud.api as fraud_api
import pcapi.core.fraud.models as fraud_models
from pcapi.core.history import api as history_api
from pcapi.core.history import models as history_models
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offers import models as offers_models
from pcapi.core.permissions import models as perm_models
from pcapi.core.subscription import models as subscription_models
import pcapi.core.subscription.api as subscription_api
from pcapi.core.subscription.models import SubscriptionItemStatus
from pcapi.core.subscription.models import SubscriptionStep
from pcapi.core.subscription.phone_validation import api as phone_validation_api
from pcapi.core.subscription.phone_validation import exceptions as phone_validation_exceptions
from pcapi.core.users import api as users_api
from pcapi.core.users import constants as users_constants
from pcapi.core.users import exceptions as users_exceptions
from pcapi.core.users import models as users_models
from pcapi.core.users import utils as users_utils
import pcapi.core.users.email.update as email_update
from pcapi.core.users.models import EligibilityType
from pcapi.models import db
from pcapi.models.beneficiary_import import BeneficiaryImport
from pcapi.models.beneficiary_import_status import BeneficiaryImportStatus
from pcapi.repository import repository
from pcapi.routes.backoffice_v3.serialization import accounts as serialization_accounts
import pcapi.utils.email as email_utils

from . import search_utils
from . import utils
from .forms import account as account_forms
from .forms import empty as empty_forms
from .forms import search as search_forms
from .forms import user as user_forms
from .serialization import accounts
from .serialization import search


public_accounts_blueprint = utils.child_backoffice_blueprint(
    "public_accounts",
    __name__,
    url_prefix="/public-accounts",
    permission=perm_models.Permissions.READ_PUBLIC_ACCOUNT,
)


@public_accounts_blueprint.route("/search", methods=["GET"])
def search_public_accounts() -> utils.BackofficeResponse:
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

    form.page.data = 1  # Reset to first page when form is submitted ("Chercher" clicked)

    return render_template(
        "accounts/search_result.html",
        search_form=form,
        search_dst=url_for(".search_public_accounts"),
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


def _convert_fraud_review_to_fraud_action_dict(fraud_review: fraud_models.BeneficiaryFraudReview) -> dict:
    return {
        "creationDate": fraud_review.dateReviewed,
        "type": "Revue manuelle",
        "applicableEligibilities": [fraud_review.eligibilityType.value]
        if fraud_review.eligibilityType is not None
        else [],
        "status": fraud_models.FraudReviewStatus(fraud_review.review).value,
        "reason": fraud_review.reason,
    }


def _convert_check_item_to_fraud_action_dict(id_check_item: accounts.IdCheckItemModel) -> dict:
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
    user = (
        users_models.User.query.filter_by(id=user_id)
        .options(
            sa.orm.joinedload(users_models.User.deposits),
            sa.orm.joinedload(users_models.User.userBookings)
            .joinedload(bookings_models.Booking.stock)
            .joinedload(offers_models.Stock.offer),
            sa.orm.joinedload(users_models.User.userBookings)
            .joinedload(bookings_models.Booking.offerer)
            .load_only(offerers_models.Offerer.name),
            sa.orm.joinedload(users_models.User.userBookings)
            .joinedload(bookings_models.Booking.venue)
            .load_only(offerers_models.Venue.bookingEmail),
            sa.orm.joinedload(users_models.User.beneficiaryFraudChecks),
            sa.orm.joinedload(users_models.User.beneficiaryFraudReviews),
            sa.orm.joinedload(users_models.User.beneficiaryImports)
            .joinedload(BeneficiaryImport.statuses)
            .joinedload(BeneficiaryImportStatus.author)
            .load_only(users_models.User.firstName, users_models.User.lastName),
            sa.orm.joinedload(users_models.User.action_history)
            .joinedload(history_models.ActionHistory.authorUser)
            .load_only(users_models.User.firstName, users_models.User.lastName),
            sa.orm.joinedload(users_models.User.email_history),
        )
        .one_or_none()
    )

    if not user:
        raise NotFound()

    domains_credit = (
        users_api.get_domains_credit(user, user_bookings=user.userBookings) if user.is_beneficiary else None
    )
    history = get_public_account_history(user)
    duplicate_user_id = None
    eligibility_history = get_eligibility_history(user)
    user_current_eligibility = users_api.get_eligibility_at_date(user.birth_date, datetime.datetime.utcnow())

    if (
        user_current_eligibility is not None and user_current_eligibility.value in eligibility_history
    ):  # get_eligibility_at_date might return None
        subscription_items = [
            item
            for item in eligibility_history[user_current_eligibility.value].subscriptionItems
            if item.type == subscription_models.SubscriptionStep.IDENTITY_CHECK.value
            and item.status != subscription_models.SubscriptionItemStatus.OK.value
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
                postal_address_autocomplete=f"{user.address}, {user.postalCode} {user.city}"
                if user.address is not None and user.city is not None and user.postalCode is not None
                else None,
                address=user.address,
                postal_code=user.postalCode,
                city=user.city,
            )

        kwargs.update(
            {
                "edit_account_form": edit_account_form,
                "edit_account_dst": url_for(".update_public_account", user_id=user.id),
                "manual_review_form": account_forms.ManualReviewForm()
                if utils.has_current_user_permission(perm_models.Permissions.BENEFICIARY_FRAUD_ACTIONS)
                else None,
                "manual_review_dst": url_for(".review_public_account", user_id=user.id),
                "send_validation_code_form": empty_forms.EmptyForm(),
                "manual_phone_validation_form": empty_forms.EmptyForm(),
            }
        )

        if not user.isEmailValidated:
            kwargs["resend_email_validation_form"] = empty_forms.EmptyForm()

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

    kwargs.update(user_forms.get_toggle_suspension_args(user))

    return render_template(
        "accounts/get.html",
        search_form=search_forms.SearchForm(),
        search_dst=url_for(".search_public_accounts"),
        user=user,
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
    eligibility_history: dict[str, accounts.EligibilitySubscriptionHistoryModel]
) -> list[serialization_accounts.IdCheckItemModel]:
    id_check_histories_desc: list[serialization_accounts.IdCheckItemModel] = []
    for history in eligibility_history.values():
        id_check_histories_desc += history.idCheckHistory
    return sorted(
        id_check_histories_desc,
        key=lambda h: h.dateCreated,
        reverse=True,
    )


class TunnelType(enum.Enum):
    NOT_ELIGIBLE = "not-eligible"
    AGE18 = EligibilityType.AGE18.value
    UNDERAGE = EligibilityType.UNDERAGE.value
    UNDERAGE_AGE18 = f"{EligibilityType.UNDERAGE.value}+{EligibilityType.AGE18.value}"


class RegistrationStepStatus(enum.Enum):
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"


def _get_tunnel_type(user: users_models.User) -> TunnelType:
    if user.birth_date is None:
        return TunnelType.NOT_ELIGIBLE

    age_at_creation = users_utils.get_age_at_date(user.birth_date, user.dateCreated)  # type: ignore [arg-type]
    age_now = users_utils.get_age_from_birth_date(user.birth_date)  # type: ignore [arg-type]

    if age_now < users_constants.ELIGIBILITY_AGE_18:
        return TunnelType.UNDERAGE
    if age_at_creation < users_constants.ELIGIBILITY_AGE_18 <= age_now:
        return TunnelType.UNDERAGE_AGE18
    if age_at_creation == users_constants.ELIGIBILITY_AGE_18:
        return TunnelType.AGE18
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
        step_id: int,
        description: str,
        subscription_item_status: str,
        icon: str,
        fraud_actions_history: list[dict] = None,
        is_active: bool = False,
        is_disabled: bool = False,
    ):
        if fraud_actions_history is not None:
            self.fraud_actions_history = fraud_actions_history
        else:
            self.fraud_actions_history = []

        self.step_id = step_id
        self.description = description
        self.subscription_item_status = subscription_item_status
        self.icon = icon
        self.status = {
            "error": _get_status(subscription_item_status) is RegistrationStepStatus.ERROR,
            "success": _get_status(subscription_item_status) is RegistrationStepStatus.SUCCESS,
            "warning": _get_status(subscription_item_status) is RegistrationStepStatus.WARNING,
            "active": is_active,
            "disabled": is_disabled,
        }

    def __eq__(self, other: object) -> bool | NotImplementedType:
        if not isinstance(other, RegistrationStep):
            return NotImplemented
        return (
            self.fraud_actions_history == other.fraud_actions_history
            and self.step_id == other.step_id
            and self.description == other.description
            and self.subscription_item_status == other.subscription_item_status
            and self.icon == other.icon
            and self.status == other.status
        )


def _get_steps_for_tunnel(
    user: users_models.User,
    tunnel_type: TunnelType,
    subscription_item_status: dict,
    id_check_histories: list,
    fraud_reviews_desc: list[fraud_models.BeneficiaryFraudReview],
) -> list[RegistrationStep]:
    item_status_15_17 = subscription_item_status[EligibilityType.UNDERAGE.value]
    item_status_18 = subscription_item_status[EligibilityType.AGE18.value]

    if tunnel_type is TunnelType.UNDERAGE:
        steps = _get_steps_tunnel_underage(user, id_check_histories, item_status_15_17, fraud_reviews_desc)
    elif tunnel_type is TunnelType.AGE18:
        steps = _get_steps_tunnel_age18(user, id_check_histories, item_status_18, fraud_reviews_desc)
    elif tunnel_type is TunnelType.UNDERAGE_AGE18:
        steps = _get_steps_tunnel_underage_age18(
            user, id_check_histories, item_status_15_17, item_status_18, fraud_reviews_desc
        )
    else:
        steps = _get_steps_tunnel_unspecified(item_status_15_17, item_status_18)

    if tunnel_type is TunnelType.NOT_ELIGIBLE:
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


def _get_steps_tunnel_unspecified(item_status_15_17: dict, item_status_18: dict) -> list[RegistrationStep]:
    if item_status_15_17 and item_status_15_17[SubscriptionStep.EMAIL_VALIDATION.value] is not None:
        email_status = item_status_15_17[SubscriptionStep.EMAIL_VALIDATION.value]
    elif item_status_18 and item_status_18[SubscriptionStep.EMAIL_VALIDATION.value] is not None:
        email_status = item_status_18[SubscriptionStep.EMAIL_VALIDATION.value]
    else:
        email_status = SubscriptionItemStatus.PENDING.value
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


def _get_steps_tunnel_underage_age18(
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
                and EligibilityType.UNDERAGE.value in id_check_history.applicable_eligibilities
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
                if id_check_history.type
                in {
                    fraud_models.FraudCheckType.UBBLE.value,
                    fraud_models.FraudCheckType.EDUCONNECT.value,
                    fraud_models.FraudCheckType.DMS.value,
                }
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
            description="Pass 15-17",
            subscription_item_status=SubscriptionItemStatus.OK.value
            if user.received_pass_15_17
            else SubscriptionItemStatus.VOID.value,
            icon="1517",
            fraud_actions_history=[
                _convert_fraud_review_to_fraud_action_dict(review)
                for review in fraud_reviews_desc
                if review.eligibilityType == EligibilityType.UNDERAGE
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
                if id_check_history.type
                in {
                    fraud_models.FraudCheckType.UBBLE.value,
                    fraud_models.FraudCheckType.DMS.value,
                    fraud_models.FraudCheckType.JOUVE.value,
                }
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
            description="Pass 18",
            subscription_item_status=SubscriptionItemStatus.OK.value
            if user.received_pass_18
            else SubscriptionItemStatus.VOID.value,
            icon="bi-card-checklist",
            fraud_actions_history=[
                _convert_fraud_review_to_fraud_action_dict(review)
                for review in fraud_reviews_desc
                if review.eligibilityType == EligibilityType.AGE18
            ],
        ),
    ]
    return steps


def _get_steps_tunnel_age18(
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
                and EligibilityType.AGE18.value in id_check_history.applicable_eligibilities
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
                and EligibilityType.AGE18.value in id_check_history.applicable_eligibilities
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
                if id_check_history.type
                in {
                    fraud_models.FraudCheckType.UBBLE.value,
                    fraud_models.FraudCheckType.DMS.value,
                    fraud_models.FraudCheckType.JOUVE.value,
                }
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
            description="Pass 18",
            subscription_item_status=SubscriptionItemStatus.OK.value
            if user.received_pass_18
            else SubscriptionItemStatus.VOID.value,
            icon="18",
            fraud_actions_history=[
                _convert_fraud_review_to_fraud_action_dict(review)
                for review in fraud_reviews_desc
                if review.eligibilityType == EligibilityType.AGE18
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
                and EligibilityType.UNDERAGE.value in id_check_history.applicable_eligibilities
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
                if id_check_history.type
                in {
                    fraud_models.FraudCheckType.UBBLE.value,
                    fraud_models.FraudCheckType.EDUCONNECT.value,
                    fraud_models.FraudCheckType.DMS.value,
                    fraud_models.FraudCheckType.JOUVE.value,
                }
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
            description="Pass 15-17",
            subscription_item_status=SubscriptionItemStatus.OK.value
            if user.received_pass_15_17
            else SubscriptionItemStatus.VOID.value,
            icon="1517",
            fraud_actions_history=[
                _convert_fraud_review_to_fraud_action_dict(review)
                for review in fraud_reviews_desc
                if review.eligibilityType == EligibilityType.AGE18
            ],
        ),
    ]
    return steps


def _get_tunnel(
    user: users_models.User,
    eligibility_history: dict[str, accounts.EligibilitySubscriptionHistoryModel],
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
    eligibility_history: dict[str, accounts.EligibilitySubscriptionHistoryModel]
) -> dict[str, dict]:
    subscription_item_status: dict[str, dict] = {EligibilityType.UNDERAGE.value: {}, EligibilityType.AGE18.value: {}}
    for key, value in eligibility_history.items():
        for item in value.subscriptionItems:
            if key is EligibilityType.UNDERAGE.value:
                subscription_item_status[EligibilityType.UNDERAGE.value][item.type] = item.status
            elif key is EligibilityType.AGE18.value:
                subscription_item_status[EligibilityType.AGE18.value][item.type] = item.status
    return subscription_item_status


def _get_progress(steps: list[RegistrationStep]) -> float:
    active_step_index = next((index for (index, s) in enumerate(steps) if s.status["active"]), None)
    progress = active_step_index * (100 / (len(steps) - 1)) if active_step_index else 0
    return progress


@public_accounts_blueprint.route("/<int:user_id>", methods=["GET"])
@utils.permission_required(perm_models.Permissions.READ_PUBLIC_ACCOUNT)
def get_public_account(user_id: int) -> utils.BackofficeResponse:
    return render_public_account_details(user_id)


@public_accounts_blueprint.route("/<int:user_id>/update", methods=["POST"])
@utils.permission_required(perm_models.Permissions.MANAGE_PUBLIC_ACCOUNT)
def update_public_account(user_id: int) -> utils.BackofficeResponse:
    user = users_models.User.query.get_or_404(user_id)

    form = account_forms.EditAccountForm()
    if not form.validate():
        flash("Le formulaire n'est pas valide", "warning")
        return render_public_account_details(user_id, form), 400

    try:
        snapshot = users_api.update_user_info(
            user,
            author=current_user,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            validated_birth_date=form.birth_date.data,
            phone_number=form.phone_number.data,
            id_piece_number=form.id_piece_number.data,
            address=form.address.data,
            postal_code=form.postal_code.data,
            city=form.city.data,
        )
    except phone_validation_exceptions.InvalidPhoneNumber:
        flash("Le numéro de téléphone est invalide", "warning")
        return render_public_account_details(user_id, form), 400

    if form.email.data and form.email.data != email_utils.sanitize_email(user.email):
        # Do not log email change in snapshot, since it is already logged in user_email_history table
        try:
            email_update.full_email_update_by_admin(user, form.email.data)
        except users_exceptions.EmailExistsError:
            form.email.errors.append("L'email est déjà associé à un autre utilisateur")
            snapshot.log_update(save=True)
            flash("L'email est déjà associé à un autre utilisateur", "warning")
            return render_public_account_details(user_id, form), 400

        # TODO (prouzet) old email should also be updated, but there is no update_external_user by email
        external_attributes_api.update_external_user(user)

    snapshot.log_update(save=True)

    flash("Informations mises à jour", "success")
    return redirect(get_public_account_link(user_id), code=303)


@public_accounts_blueprint.route("/<int:user_id>/resend-validation-email", methods=["POST"])
@utils.permission_required(perm_models.Permissions.MANAGE_PUBLIC_ACCOUNT)
def resend_validation_email(user_id: int) -> utils.BackofficeResponse:
    user = users_models.User.query.get_or_404(user_id)

    if user.has_admin_role or user.has_pro_role:
        flash("Cette action n'est pas supportée pour les utilisateurs admin ou pro", "warning")
    elif user.isEmailValidated:
        flash("L'adresse email est déjà validée", "warning")
    else:
        users_api.request_email_confirmation(user)
        flash("Email de validation envoyé", "success")

    return redirect(get_public_account_link(user_id), code=303)


@public_accounts_blueprint.route("/<int:user_id>/validate-phone-number", methods=["POST"])
@utils.permission_required(perm_models.Permissions.MANAGE_PUBLIC_ACCOUNT)
def manually_validate_phone_number(user_id: int) -> utils.BackofficeResponse:
    user = users_models.User.query.get_or_404(user_id)
    if not user.phoneNumber:
        flash("L'utilisateur n'a pas de numéro de téléphone", "warning")
        return redirect(get_public_account_link(user_id), code=303)

    user.phoneValidationStatus = users_models.PhoneValidationStatusType.VALIDATED
    action = history_api.log_action(
        action_type=history_models.ActionType.USER_PHONE_VALIDATED, author=current_user, user=user
    )
    repository.save(user, action)

    subscription_api.activate_beneficiary_if_no_missing_step(user)
    users_api.delete_all_users_phone_validation_tokens(user)

    flash("Le numéro a été validé avec succès", "success")

    return redirect(get_public_account_link(user_id), code=303)


@public_accounts_blueprint.route("/<int:user_id>/send-validation-code", methods=["POST"])
@utils.permission_required(perm_models.Permissions.MANAGE_PUBLIC_ACCOUNT)
def send_validation_code(user_id: int) -> utils.BackofficeResponse:
    user = users_models.User.query.get_or_404(user_id)

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
@utils.permission_required(perm_models.Permissions.BENEFICIARY_FRAUD_ACTIONS)
def review_public_account(user_id: int) -> utils.BackofficeResponse:
    user = users_models.User.query.get_or_404(user_id)

    form = account_forms.ManualReviewForm()
    if not form.validate():
        flash("Les données envoyées comportent des erreurs", "warning")
        return redirect(url_for("backoffice_v3_web.public_accounts.get_public_account", user_id=user_id), code=303)

    try:
        fraud_api.validate_beneficiary(
            user=user,
            reviewer=current_user,
            reason=form.reason.data,
            review=fraud_models.FraudReviewStatus(form.status.data),
            reviewed_eligibility=users_models.EligibilityType[form.eligibility.data],
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

    return redirect(get_public_account_link(user_id), code=303)


@public_accounts_blueprint.route("/<int:user_id>/comment", methods=["POST"])
@utils.permission_required(perm_models.Permissions.MANAGE_PUBLIC_ACCOUNT)
def comment_public_account(user_id: int) -> utils.BackofficeResponse:
    user = users_models.User.query.get_or_404(user_id)

    form = account_forms.CommentForm()
    if not form.validate():
        flash("Les données envoyées comportent des erreurs", "warning")
    else:
        users_api.add_comment_to_user(user=user, author_user=current_user, comment=form.comment.data)
        flash("Commentaire enregistré", "success")

    return redirect(get_public_account_link(user_id, active_tab="history"), code=303)


def fetch_rows(search_model: search.SearchUserModel) -> Pagination:
    return search_utils.fetch_paginated_rows(users_api.search_public_account, search_model)


def get_public_account_link(user_id: int, **kwargs: typing.Any) -> str:
    return url_for("backoffice_v3_web.public_accounts.get_public_account", user_id=user_id, **kwargs)


def get_eligibility_history(user: users_models.User) -> dict[str, accounts.EligibilitySubscriptionHistoryModel]:
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
        age_at_creation = users_utils.get_age_at_date(user.birth_date, user.dateCreated)  # type: ignore [arg-type]
        if age_at_creation <= users_constants.ELIGIBILITY_AGE_18:
            if age_at_creation == users_constants.ELIGIBILITY_AGE_18:
                eligibility_types.append(users_models.EligibilityType.AGE18)
                if users_models.EligibilityType.UNDERAGE in [
                    fraud_check.eligibilityType for fraud_check in user.beneficiaryFraudChecks
                ]:
                    eligibility_types.insert(0, users_models.EligibilityType.UNDERAGE)
            else:
                eligibility_types.append(users_models.EligibilityType.UNDERAGE)
                age_now = users_utils.get_age_from_birth_date(user.birth_date)  # type: ignore [arg-type]
                if age_now >= users_constants.ELIGIBILITY_AGE_18 or users_models.EligibilityType.AGE18 in [
                    fraud_check.eligibilityType for fraud_check in user.beneficiaryFraudChecks
                ]:
                    eligibility_types.append(users_models.EligibilityType.AGE18)
    else:
        # Profile completion step not reached yet; can't guess eligibility, display all
        eligibility_types = list(users_models.EligibilityType)

    for eligibility in eligibility_types:
        subscriptions[eligibility.value] = accounts.EligibilitySubscriptionHistoryModel(
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


def _get_latest_fraud_check(
    eligibility_history: dict[str, accounts.EligibilitySubscriptionHistoryModel],
    check_types: list[fraud_models.FraudCheckType],
) -> accounts.IdCheckItemModel | None:
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
    eligibility_history: dict[str, accounts.EligibilitySubscriptionHistoryModel],
) -> str | None:
    for history_item in eligibility_history.values():
        check_history_items = sorted(history_item.idCheckHistory, key=attrgetter("dateCreated"), reverse=True)
        for check_history in check_history_items:
            reason_codes = check_history.reasonCodes if check_history.reasonCodes else None

            if reason_codes and (
                fraud_models.FraudReasonCode.DUPLICATE_USER.value in reason_codes
                or fraud_models.FraudReasonCode.DUPLICATE_ID_PIECE_NUMBER.value in reason_codes
            ):
                if check_history.reason:
                    id_searched = re.search(r"\s(\d+)\D*$", check_history.reason)
                    if id_searched:
                        return id_searched.group(1)
    return None


def get_public_account_history(user: users_models.User) -> list[accounts.AccountAction | history_models.ActionHistory]:
    # All data should have been joinloaded with user
    history: list[history_models.ActionHistory | accounts.AccountAction] = list(user.action_history)

    if history_models.ActionType.USER_CREATED not in (action.actionType for action in user.action_history):
        history.append(accounts.AccountCreatedAction(user))

    for change in user.email_history:
        history.append(accounts.EmailChangeAction(change))

    for fraud_check in user.beneficiaryFraudChecks:
        history.append(accounts.FraudCheckAction(fraud_check))

    for review in user.beneficiaryFraudReviews:
        history.append(accounts.ReviewAction(review))

    for import_ in user.beneficiaryImports:
        for status in import_.statuses:
            history.append(accounts.ImportStatusAction(import_, status))

    history = sorted(history, key=lambda item: item.actionDate or datetime.datetime.min, reverse=True)

    return history
