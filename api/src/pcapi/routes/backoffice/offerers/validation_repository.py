"""
# Queries are very specific to backoffice routes, so they are not part of pcapi.core.offerers.api
"""

import re
from datetime import datetime

import sqlalchemy as sa
import sqlalchemy.orm as sa_orm

from pcapi.connectors.dms.models import GraphQLApplicationStates
from pcapi.core.educational import models as educational_models
from pcapi.core.geography import models as geography_models
from pcapi.core.history import models as history_models
from pcapi.core.offerers import api as offerers_api
from pcapi.core.offerers import models as offerers_models
from pcapi.core.users import models as users_models
from pcapi.models import db
from pcapi.models.api_errors import ApiErrors
from pcapi.models.validation_status_mixin import ValidationStatus
from pcapi.utils import email as email_utils
from pcapi.utils import siren as siren_utils
from pcapi.utils import string as string_utils
from pcapi.utils.clean_accents import clean_accents
from pcapi.utils.regions import get_department_codes_for_region


def _join_venue(query: sa_orm.Query, is_venue_table_joined: bool = False) -> tuple[sa_orm.Query, bool]:
    if not is_venue_table_joined:
        query = query.join(offerers_models.Venue)
    return query, True


def _build_address_filter(condition: sa.ColumnElement[bool]) -> sa.Exists:
    return (
        sa.exists()
        .where(offerers_models.Venue.managingOffererId == offerers_models.Offerer.id)
        .where(offerers_models.Venue.siret.is_not(None))
        .where(offerers_models.OffererAddress.id == offerers_models.Venue.offererAddressId)
        .where(geography_models.Address.id == offerers_models.OffererAddress.addressId)
        .where(condition)
    )


def _apply_query_filters(
    query: sa_orm.Query,
    *,
    q: str | None,  # search query
    regions: list[str] | None,
    tags: list[offerers_models.OffererTag] | None,
    status: list[ValidationStatus] | None,
    dms_adage_status: list[GraphQLApplicationStates] | None,
    from_datetime: datetime | None,
    to_datetime: datetime | None,
    offerers_id: list[int] | None,
    user_offerers_id: list[int] | None,
    cls: type[offerers_models.Offerer | offerers_models.UserOfferer],
    offerer_id_column: sa_orm.InstrumentedAttribute,
) -> sa_orm.Query:
    is_venue_table_joined = False

    if status:
        query = query.filter(cls.validationStatus.in_(status))

    if dms_adage_status:
        query = query.join(
            educational_models.CollectiveDmsApplication,
            offerers_models.Offerer.siren == educational_models.CollectiveDmsApplication.siren,
        ).filter(
            educational_models.CollectiveDmsApplication.state.in_(
                [GraphQLApplicationStates[str(state)].value for state in dms_adage_status]
            )
        )

    if tags:
        tagged_offerers = (
            sa.select(offerers_models.Offerer.id, sa.func.array_agg(offerers_models.OffererTag.id).label("tags"))
            .join(
                offerers_models.OffererTagMapping,
                offerers_models.OffererTagMapping.offererId == offerers_models.Offerer.id,
            )
            .join(
                offerers_models.OffererTag,
                offerers_models.OffererTag.id == offerers_models.OffererTagMapping.tagId,
            )
            .group_by(
                offerers_models.Offerer.id,
            )
            .cte()
        )

        query = query.join(tagged_offerers, tagged_offerers.c.id == offerer_id_column).filter(
            sa.and_(*(tagged_offerers.c.tags.any(tag.id) for tag in tags))
        )

    if from_datetime:
        query = query.filter(cls.dateCreated >= from_datetime)

    if to_datetime:
        query = query.filter(cls.dateCreated <= to_datetime)

    if regions:
        department_codes: list[str] = []
        for region in regions:
            department_codes += get_department_codes_for_region(region)
        # At least one managed with SIRET venue in selected regions
        query = query.filter(_build_address_filter(geography_models.Address.departmentCode.in_(department_codes)))

    if q:
        sanitized_q = email_utils.sanitize_email(q)

        if string_utils.is_numeric(sanitized_q):
            num_digits = len(sanitized_q)
            # for dmsToken containing digits only
            if num_digits == 12:
                query, is_venue_table_joined = _join_venue(query, is_venue_table_joined)
                query = query.filter(offerers_models.Venue.dmsToken == sanitized_q)
            elif num_digits == siren_utils.SIREN_LENGTH:
                query = query.filter(offerers_models.Offerer.siren == sanitized_q)
            elif num_digits == siren_utils.RID7_LENGTH:
                query = query.filter(offerers_models.Offerer.siren == siren_utils.rid7_to_siren(sanitized_q))
            elif num_digits == 5:
                query = query.filter(_build_address_filter(geography_models.Address.postalCode == sanitized_q))
            elif num_digits in (2, 3):
                query = query.filter(_build_address_filter(geography_models.Address.departmentCode == sanitized_q))
            else:
                raise ApiErrors(
                    {
                        "q": [
                            "Le nombre de chiffres ne correspond pas à un SIREN, code postal, département ou ID DMS CB"
                        ]
                    },
                    status_code=400,
                )
        elif email_utils.is_valid_email(sanitized_q):
            query = query.filter(users_models.User.email == sanitized_q)
        # We theoretically can have venues which name is 12 letters between a and f
        # But it never happened in the database, and it's costly to handle
        elif dms_token_term := re.match(offerers_api.DMS_TOKEN_REGEX, q):
            query, is_venue_table_joined = _join_venue(query, is_venue_table_joined)
            query = query.filter(offerers_models.Venue.dmsToken == dms_token_term.group(1).lower())
        else:
            name_query = "%{}%".format(clean_accents(q))
            # UNION is really faster than OR when filtering on different tables (verified experimentally):
            # - everything in `OR` => sequential scan on offerer
            # - using `UNION` to split between offerer conditions and user condition => index scan
            query = query.filter(
                sa.or_(
                    sa.func.immutable_unaccent(offerers_models.Offerer.name).ilike(name_query),
                    _build_address_filter(sa.func.immutable_unaccent(geography_models.Address.city).ilike(name_query)),
                )
            ).union(
                query.filter(
                    sa.func.immutable_unaccent(users_models.User.firstName + " " + users_models.User.lastName).ilike(
                        name_query
                    )
                )
            )

    if offerers_id:
        query = query.filter(offerers_models.Offerer.id.in_(offerers_id))
    if user_offerers_id:
        query = query.filter(offerers_models.UserOfferer.id.in_(user_offerers_id))

    return query


def _get_homologation_tags_subquery() -> sa.sql.selectable.ScalarSelect:
    return (
        _get_tags_subquery()
        .join(offerers_models.OffererTagCategoryMapping)
        .join(offerers_models.OffererTagCategory)
        .filter(offerers_models.OffererTagCategory.name == "homologation")
    )


def _get_tags_subquery() -> sa.sql.selectable.ScalarSelect:
    # Aggregate tags as a json dictionary returned in a single row (joinedload would fetch 1 result row per tag)
    # For a single offerer, column value is like:
    # [{'name': 'top-acteur', 'label': 'Top Acteur'}, {'name': 'culture-scientifique', 'label': 'Culture scientifique'}]
    return (
        sa.select(
            sa.func.jsonb_agg(
                sa.func.jsonb_build_object(
                    "name",
                    offerers_models.OffererTag.name,
                    "label",
                    offerers_models.OffererTag.label,
                )
            )
        )
        .select_from(offerers_models.OffererTag)
        .join(offerers_models.OffererTagMapping)
        .filter(offerers_models.OffererTagMapping.offererId == offerers_models.Offerer.id)
        .correlate(offerers_models.Offerer)
        .scalar_subquery()
    )


def list_offerers_to_be_validated(
    *,
    q: str | None = None,  # search query
    regions: list[str] | None = None,
    tags: list[offerers_models.OffererTag] | None = None,
    status: list[ValidationStatus] | None = None,
    ae_documents_received: list[bool] | None = None,
    last_instructor_ids: list[int] | None = None,
    dms_adage_status: list[GraphQLApplicationStates] | None = None,
    from_datetime: datetime | None = None,
    to_datetime: datetime | None = None,
    offerers_id: list[int] | None = None,
) -> sa_orm.Query:
    # Fetch only the single last comment to avoid loading the full history (joinedload would fetch 1 row per action)
    # This replaces lookup for last comment in offerer.action_history after joining with all actions
    last_comment_subquery = (
        db.session.query(history_models.ActionHistory.comment)
        .filter(
            history_models.ActionHistory.offererId == offerers_models.Offerer.id,
            history_models.ActionHistory.comment.is_not(None),
            history_models.ActionHistory.actionType.in_(
                [
                    history_models.ActionType.OFFERER_NEW,
                    history_models.ActionType.OFFERER_PENDING,
                    history_models.ActionType.OFFERER_VALIDATED,
                    history_models.ActionType.OFFERER_REJECTED,
                    history_models.ActionType.OFFERER_CLOSED,
                    history_models.ActionType.COMMENT,
                ]
            ),
            history_models.ActionHistory.userId.is_(None),
        )
        .order_by(history_models.ActionHistory.actionDate.desc())
        .limit(1)
        .correlate(offerers_models.Offerer)
        .scalar_subquery()
    )

    # Ensure that we join with a single user, not on all attached users (would also multiply the number of rows)
    # the oldest entry in the table
    creator_user_offerer_id = (
        db.session.query(offerers_models.UserOfferer.id)
        .filter(
            offerers_models.UserOfferer.offererId == offerers_models.Offerer.id,
        )
        .order_by(offerers_models.UserOfferer.id.asc())
        .limit(1)
        .correlate(offerers_models.Offerer)
        .scalar_subquery()
    )

    # Aggregate venues with DMS applications, as a json dictionary returned in a single row
    # For a single offerer, column value is like:
    # [{'id': 40, 'name': 'accepted_dms eac_with_two_adage_venues', 'siret': '42883745400057', 'state': 'accepte', 'lastChangeDate': 'datetime'},
    # {'id': 41, 'name': 'rejected_dms eac_with_two_adage_venues', 'siret': '42883745400058', 'state': 'refuse', 'lastChangeDate': 'datetime'}]
    dms_applications_subquery = (
        sa.select(
            sa.func.jsonb_agg(
                sa.func.jsonb_build_object(
                    "id",
                    educational_models.CollectiveDmsApplication.id,
                    "siret",
                    educational_models.CollectiveDmsApplication.siret,
                    "name",
                    offerers_models.Venue.common_name,
                    "state",
                    educational_models.CollectiveDmsApplication.state,
                    "lastChangeDate",
                    educational_models.CollectiveDmsApplication.lastChangeDate,
                )
            )
        )
        .select_from(educational_models.CollectiveDmsApplication)
        .outerjoin(
            offerers_models.Venue, offerers_models.Venue.siret == educational_models.CollectiveDmsApplication.siret
        )
        .filter(offerers_models.Offerer.siren == educational_models.CollectiveDmsApplication.siren)
        .correlate(offerers_models.Offerer)
        .scalar_subquery()
    )

    base_query = (
        db.session.query(
            offerers_models.Offerer,
            _get_tags_subquery().label("tags"),
            last_comment_subquery.label("last_comment"),
            users_models.User.id.label("creator_id"),
            users_models.User.full_name.label("creator_name"),
            users_models.User.email.label("creator_email"),
            dms_applications_subquery.label("dms_venues"),
        )
        .outerjoin(offerers_models.UserOfferer, offerers_models.UserOfferer.id == creator_user_offerer_id)
        .outerjoin(users_models.User, offerers_models.UserOfferer.user)
        .options(
            sa_orm.with_expression(offerers_models.Offerer.cities, offerers_models.Offerer.cities_expression()),
        )
    )

    query = _apply_query_filters(
        base_query,
        q=q,
        regions=regions,
        tags=tags,
        status=status,
        dms_adage_status=dms_adage_status,
        from_datetime=from_datetime,
        to_datetime=to_datetime,
        offerers_id=offerers_id,
        user_offerers_id=None,
        cls=offerers_models.Offerer,
        offerer_id_column=offerers_models.Offerer.id,
    )

    # after _apply_query_filters so that outerjoin below is after union (not required for filters),
    # otherwise sqlalchemy raises "cartesian product" error in case of free text search.
    query = query.outerjoin(
        offerers_models.IndividualOffererSubscription, offerers_models.Offerer.individualSubscription
    ).options(
        sa_orm.contains_eager(offerers_models.Offerer.individualSubscription).load_only(
            offerers_models.IndividualOffererSubscription.isEmailSent,
            offerers_models.IndividualOffererSubscription.isCriminalRecordReceived,
            offerers_models.IndividualOffererSubscription.isExperienceReceived,
        ),
    )

    if ae_documents_received:
        query = query.filter(
            offerers_models.IndividualOffererSubscription.isEmailSent.is_(True),
            sa.and_(
                offerers_models.IndividualOffererSubscription.isCriminalRecordReceived.is_(True),
                offerers_models.IndividualOffererSubscription.isExperienceReceived.is_(True),
            ).in_(ae_documents_received),
        )

    if last_instructor_ids:
        query = query.filter(
            db.session.query(history_models.ActionHistory.authorUserId)
            .filter(
                history_models.ActionHistory.offererId == offerers_models.Offerer.id,
                history_models.ActionHistory.actionType.in_(
                    (
                        history_models.ActionType.OFFERER_PENDING,
                        history_models.ActionType.OFFERER_VALIDATED,
                        history_models.ActionType.OFFERER_REJECTED,
                        history_models.ActionType.OFFERER_CLOSED,
                    )
                ),
            )
            .order_by(history_models.ActionHistory.actionDate.desc())
            .limit(1)
            .scalar_subquery()
            .in_(last_instructor_ids)
        )

    return query.distinct()


def list_users_offerers_to_be_validated(
    *,
    q: str | None = None,  # search query
    regions: list[str] | None = None,
    tags: list[offerers_models.OffererTag] | None = None,
    status: list[ValidationStatus] | None = None,
    last_instructor_ids: list[int] | None = None,
    offerer_status: list[ValidationStatus] | None = None,
    from_datetime: datetime | None = None,
    to_datetime: datetime | None = None,
    user_offerers_ids: list[int] | None = None,
) -> sa_orm.Query:
    # Fetch only the single last comment to avoid loading the full history (joinedload would fetch 1 row per action)
    last_comment_subquery = (
        db.session.query(history_models.ActionHistory.comment)
        .filter(
            history_models.ActionHistory.offererId == offerers_models.Offerer.id,
            history_models.ActionHistory.userId == users_models.User.id,
            history_models.ActionHistory.comment.is_not(None),
            history_models.ActionHistory.actionType.in_(
                [
                    history_models.ActionType.USER_OFFERER_NEW,
                    history_models.ActionType.USER_OFFERER_PENDING,
                    history_models.ActionType.USER_OFFERER_VALIDATED,
                    history_models.ActionType.USER_OFFERER_REJECTED,
                    history_models.ActionType.USER_OFFERER_DELETED,
                    history_models.ActionType.COMMENT,
                ]
            ),
        )
        .order_by(history_models.ActionHistory.actionDate.desc())
        .limit(1)
        .correlate(offerers_models.Offerer, users_models.User)
        .scalar_subquery()
    )

    # Fetch a single user email from attachments instead of joinedloading with all UserOfferers and Users
    creator_email_subquery = (
        db.session.query(users_models.User.email)
        .select_from(offerers_models.UserOfferer)
        .join(offerers_models.UserOfferer.user)
        .filter(offerers_models.UserOfferer.offererId == offerers_models.Offerer.id)
        .order_by(offerers_models.UserOfferer.id.asc())
        .limit(1)
        .correlate(offerers_models.Offerer)
        .scalar_subquery()
    )

    query = (
        db.session.query(
            offerers_models.UserOfferer,
            _get_homologation_tags_subquery().label("tags"),
            last_comment_subquery.label("last_comment"),
            creator_email_subquery.label("creator_email"),
        )
        .options(
            # 1-1 relationship so joinedload will not increase the number of SQL rows
            sa_orm.joinedload(offerers_models.UserOfferer.user),
            sa_orm.joinedload(offerers_models.UserOfferer.offerer),
        )
        .join(offerers_models.UserOfferer.user)
        .join(offerers_models.UserOfferer.offerer)
    )

    if offerer_status:
        query = query.filter(offerers_models.Offerer.validationStatus.in_(offerer_status))

    query = _apply_query_filters(
        query,
        q=q,
        regions=regions,
        tags=tags,
        status=status,
        dms_adage_status=None,  # no dms_adage_status for UserOfferer
        from_datetime=from_datetime,
        to_datetime=to_datetime,
        offerers_id=None,
        user_offerers_id=user_offerers_ids,
        cls=offerers_models.UserOfferer,
        offerer_id_column=offerers_models.UserOfferer.offererId,
    )

    if last_instructor_ids:
        query = query.filter(
            db.session.query(history_models.ActionHistory.authorUserId)
            .filter(
                history_models.ActionHistory.userId == offerers_models.UserOfferer.userId,
                history_models.ActionHistory.offererId == offerers_models.UserOfferer.offererId,
                history_models.ActionHistory.actionType.in_(
                    (
                        history_models.ActionType.USER_OFFERER_PENDING,
                        history_models.ActionType.USER_OFFERER_VALIDATED,
                        history_models.ActionType.USER_OFFERER_REJECTED,
                    )
                ),
            )
            .order_by(history_models.ActionHistory.actionDate.desc())
            .limit(1)
            .scalar_subquery()
            .in_(last_instructor_ids)
        )
    return query
