"""
# Queries are very specific to backoffice routes, so they are not part of pcapi.core.offerers.api
"""

from datetime import datetime
import re

import sqlalchemy as sa

from pcapi.connectors.dms.models import GraphQLApplicationStates
from pcapi.core.educational import models as educational_models
from pcapi.core.history import models as history_models
from pcapi.core.offerers import api as offerers_api
from pcapi.core.offerers import models as offerers_models
from pcapi.core.users import models as users_models
from pcapi.models import db
from pcapi.models.api_errors import ApiErrors
from pcapi.models.validation_status_mixin import ValidationStatus
from pcapi.utils import email as email_utils
from pcapi.utils.clean_accents import clean_accents
from pcapi.utils.regions import get_department_codes_for_region


def _join_venue(query: sa.orm.Query, is_venue_table_joined: bool = False) -> tuple[sa.orm.Query, bool]:
    if not is_venue_table_joined:
        query = query.join(offerers_models.Venue)
    return query, True


def _apply_query_filters(
    query: sa.orm.Query,
    q: str | None,  # search query
    regions: list[str] | None,
    tags: list[offerers_models.OffererTag] | None,
    status: list[ValidationStatus] | None,
    dms_adage_status: list[GraphQLApplicationStates] | None,
    from_datetime: datetime | None,
    to_datetime: datetime | None,
    cls: type[offerers_models.Offerer | offerers_models.UserOfferer],
    offerer_id_column: sa.orm.InstrumentedAttribute,
) -> sa.orm.Query:
    is_venue_table_joined = False

    if status:
        query = query.filter(cls.validationStatus.in_(status))

    if dms_adage_status:
        query, is_venue_table_joined = _join_venue(query, is_venue_table_joined)
        query = query.join(
            educational_models.CollectiveDmsApplication, offerers_models.Venue.collectiveDmsApplications
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
        query = query.filter(offerers_models.Offerer.departementCode.in_(department_codes))  # type: ignore [attr-defined]

    if q:
        sanitized_q = email_utils.sanitize_email(q)

        if sanitized_q.isnumeric():
            num_digits = len(sanitized_q)
            # for dmsToken containing digits only
            if num_digits == 12:
                query, is_venue_table_joined = _join_venue(query, is_venue_table_joined)
                query = query.filter(offerers_models.Venue.dmsToken == sanitized_q)
            elif num_digits == 9:
                query = query.filter(offerers_models.Offerer.siren == sanitized_q)
            elif num_digits == 5:
                query = query.filter(offerers_models.Offerer.postalCode == sanitized_q)
            elif num_digits in (2, 3):
                query = query.filter(offerers_models.Offerer.departementCode == sanitized_q)
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
                    sa.func.immutable_unaccent(offerers_models.Offerer.city).ilike(name_query),
                )
            ).union(
                query.filter(
                    sa.func.immutable_unaccent(users_models.User.firstName + " " + users_models.User.lastName).ilike(
                        name_query
                    )
                )
            )

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
    q: str | None,  # search query
    regions: list[str] | None = None,
    tags: list[offerers_models.OffererTag] | None = None,
    status: list[ValidationStatus] | None = None,
    last_instructor_ids: list[int] | None = None,
    dms_adage_status: list[GraphQLApplicationStates] | None = None,
    from_datetime: datetime | None = None,
    to_datetime: datetime | None = None,
) -> sa.orm.Query:
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
    # [{'id': 40, 'name': 'accepted_dms eac_with_two_adage_venues', 'siret': '42883745400057', 'state': 'accepte'},
    # {'id': 41, 'name': 'rejected_dms eac_with_two_adage_venues', 'siret': '42883745400058', 'state': 'refuse'}]
    dms_applications_subquery = (
        sa.select(
            sa.func.jsonb_agg(
                sa.func.jsonb_build_object(
                    "id",
                    offerers_models.Venue.id,
                    "siret",
                    offerers_models.Venue.siret,
                    "name",
                    offerers_models.Venue.common_name,
                    "state",
                    offerers_models.Venue.dms_adage_status,
                )
            )
        )
        .select_from(offerers_models.Venue)
        .filter(
            offerers_models.Venue.managingOffererId == offerers_models.Offerer.id,
            offerers_models.Venue.dms_adage_status.is_not(None),  # type: ignore [attr-defined]
        )
        .correlate(offerers_models.Offerer)
        .scalar_subquery()
    )

    query = (
        db.session.query(
            offerers_models.Offerer,
            _get_tags_subquery().label("tags"),
            last_comment_subquery.label("last_comment"),
            users_models.User.id.label("creator_id"),
            users_models.User.full_name.label("creator_name"),  # type: ignore [attr-defined]
            users_models.User.email.label("creator_email"),
            dms_applications_subquery.label("dms_venues"),
        )
        .outerjoin(offerers_models.UserOfferer, offerers_models.UserOfferer.id == creator_user_offerer_id)
        .outerjoin(users_models.User, offerers_models.UserOfferer.user)
        .options(
            sa.orm.joinedload(offerers_models.Offerer.individualSubscription).load_only(
                offerers_models.IndividualOffererSubscription.isEmailSent,
                offerers_models.IndividualOffererSubscription.isCriminalRecordReceived,
                offerers_models.IndividualOffererSubscription.isCertificateReceived,
            ),
        )
    )

    query = _apply_query_filters(
        query,
        q,
        regions,
        tags,
        status,
        dms_adage_status,
        from_datetime,
        to_datetime,
        offerers_models.Offerer,
        offerers_models.Offerer.id,
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
    q: str | None,  # search query
    regions: list[str] | None = None,
    tags: list[offerers_models.OffererTag] | None = None,
    status: list[ValidationStatus] | None = None,
    last_instructor_ids: list[int] | None = None,
    offerer_status: list[ValidationStatus] | None = None,
    from_datetime: datetime | None = None,
    to_datetime: datetime | None = None,
) -> sa.orm.Query:
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
            sa.orm.joinedload(offerers_models.UserOfferer.user),
            sa.orm.joinedload(offerers_models.UserOfferer.offerer),
        )
        .join(offerers_models.UserOfferer.user)
        .join(offerers_models.UserOfferer.offerer)
    )

    if offerer_status:
        query = query.filter(offerers_models.Offerer.validationStatus.in_(offerer_status))

    query = _apply_query_filters(
        query,
        q,
        regions,
        tags,
        status,
        None,  # no dms_adage_status for UserOfferer
        from_datetime,
        to_datetime,
        offerers_models.UserOfferer,
        offerers_models.UserOfferer.offererId,
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
