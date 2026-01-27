import dataclasses
import datetime
import decimal
import enum
import functools
import logging
import re
import typing
from collections import namedtuple
from io import BytesIO

import sqlalchemy as sa
import sqlalchemy.orm as sa_orm
from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import send_file
from flask import url_for
from flask_login import current_user
from markupsafe import Markup
from markupsafe import escape
from sqlalchemy.dialects import postgresql
from werkzeug.datastructures import MultiDict
from werkzeug.exceptions import NotFound

from pcapi.core import search
from pcapi.core.bookings import api as bookings_api
from pcapi.core.bookings import models as bookings_models
from pcapi.core.bookings import repository as booking_repository
from pcapi.core.categories import subcategories
from pcapi.core.criteria import models as criteria_models
from pcapi.core.external.compliance_backends import compliance_backend
from pcapi.core.finance import api as finance_api
from pcapi.core.finance import models as finance_models
from pcapi.core.geography import models as geography_models
from pcapi.core.highlights import models as highlights_models
from pcapi.core.mails import transactional as transactional_mails
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offerers import repository as offerers_repository
from pcapi.core.offers import api as offers_api
from pcapi.core.offers import exceptions as offers_exceptions
from pcapi.core.offers import models as offers_models
from pcapi.core.permissions import models as perm_models
from pcapi.core.providers import models as providers_models
from pcapi.core.search import search_offer_ids
from pcapi.core.search.models import IndexationReason
from pcapi.core.users import models as users_models
from pcapi.models import db
from pcapi.models.offer_mixin import OfferValidationStatus
from pcapi.models.offer_mixin import OfferValidationType
from pcapi.routes.backoffice import utils
from pcapi.routes.backoffice.filters import format_amount
from pcapi.routes.backoffice.filters import pluralize
from pcapi.routes.backoffice.forms import empty as empty_forms
from pcapi.routes.backoffice.pro.utils import get_connect_as
from pcapi.tasks.serialization.compliance_tasks import SearchOffersRequest
from pcapi.utils import date as date_utils
from pcapi.utils import regions as regions_utils
from pcapi.utils import string as string_utils
from pcapi.utils import urls
from pcapi.utils.requests import ExternalAPIException
from pcapi.utils.transaction_manager import mark_transaction_as_invalid
from pcapi.utils.transaction_manager import on_commit

from . import forms


list_offers_blueprint = utils.child_backoffice_blueprint(
    "offer",
    __name__,
    url_prefix="/pro/offer",
    permission=perm_models.Permissions.READ_OFFERS,
)

logger = logging.getLogger(__name__)

SEARCH_FIELD_TO_PYTHON: dict[str, dict[str, typing.Any]] = {
    "ADDRESS": {
        "field": "address",
        "column": offerers_models.OffererAddress.addressId,
        "inner_join": "offerer_address",
    },
    "CATEGORY": {
        "field": "category",
        "column": offers_models.Offer.subcategoryId,
        "facet": "offer.subcategoryId",
        "llm_filter": "offer_category_id",
        "special": lambda categories: [
            subcategory.id for subcategory in subcategories.ALL_SUBCATEGORIES if subcategory.category.id in categories
        ],
        "algolia_special": lambda categories: [
            subcategory.id for subcategory in subcategories.ALL_SUBCATEGORIES if subcategory.category.id in categories
        ],
    },
    "CREATION_DATE": {
        "field": "date",
        "llm_filter": "offer_creation_date",
        "llm_special": lambda d: d.isoformat() if d else None,
        "column": offers_models.Offer.dateCreated,
    },
    "DATE": {
        "field": "date",
        "facet": "offer.dates",
    },
    "DEPARTMENT": {
        "field": "department",
        "llm_filter": "venue_departement_code",
        "column": geography_models.Address.departmentCode,
        "facet": "venue.departmentCode",  # FIXME (prouzet, 2025-08-14): user offer address when it is sent to Algolia
        "inner_join": "address",
    },
    "REGION": {
        "field": "region",
        "column": geography_models.Address.departmentCode,
        "facet": "venue.departmentCode",  # FIXME (prouzet, 2025-08-14): user offer address when it is sent to Algolia
        "inner_join": "address",
        "special": regions_utils.get_department_codes_for_regions,
        "algolia_special": regions_utils.get_department_codes_for_regions,
    },
    "EAN": {
        "field": "string",
        "column": offers_models.Offer.ean,
        "facet": "offer.ean",
        "special": string_utils.format_ean_or_visa,
        "algolia_special": string_utils.format_ean_or_visa,
    },
    "EVENT_DATE": {
        "field": "date",
        "llm_filter": "stock_beginning_date",
        "llm_special": lambda d: d.isoformat() if d else None,
        "column": offers_models.Stock.beginningDatetime,
        "subquery_join": "stock",
    },
    "BOOKING_LIMIT_DATE": {
        "field": "date",
        "column": offers_models.Stock.bookingLimitDatetime,
        "subquery_join": "stock",
    },
    "ID": {
        "field": "string",
        "column": offers_models.Offer.id,
        "special": lambda q: [int(id_) for id_ in re.findall(r"\d+", q or "")],
    },
    "PRODUCT": {
        "field": "integer",
        "column": offers_models.Offer.productId,
        "special": lambda i: db.session.query(offers_models.Offer.productId)
        .filter(offers_models.Offer.id == i)
        .scalar_subquery(),
    },
    "NAME": {
        "field": "string",
        "column": offers_models.Offer.name,
    },
    "OFFERER": {
        "field": "offerer",
        "column": offerers_models.Venue.managingOffererId,
        "facet": "venue.id",
        "algolia_special": offerers_repository.get_venue_ids_by_offerer_ids,
        "inner_join": "venue",
    },
    "TAG": {
        "field": "criteria",
        "column": criteria_models.Criterion.id,
        "inner_join": "criterion",  # applied only when no custom filter (with operator IN)
        "outer_join": "offer_criterion",
        "outer_join_column": criteria_models.OfferCriterion.offerId,
        "custom_filters": {
            "NOT_IN": lambda values: (
                sa.exists()
                .where(
                    sa.and_(
                        criteria_models.OfferCriterion.offerId == offers_models.Offer.id,
                        criteria_models.OfferCriterion.criterionId.in_(values),
                    )
                )
                .is_(False)
            )
        },
    },
    "VENUE_TAG": {
        "field": "criteria",
        "column": offerers_models.VenueCriterion.criterionId,
        "inner_join": "venue_criterion",
        "custom_filters_inner_joins": {
            "NOT_IN": ["venue"],
            "NOT_EXIST": ["venue"],
        },
        "custom_filters": {
            "NOT_IN": lambda values: (
                sa.exists()
                .where(
                    sa.and_(
                        criteria_models.VenueCriterion.venueId == offerers_models.Venue.id,
                        criteria_models.VenueCriterion.criterionId.in_(values),
                    )
                )
                .correlate(offerers_models.Venue)
                .is_(False)
            ),
            "NOT_EXIST": lambda values: (
                sa.exists()
                .where(
                    criteria_models.VenueCriterion.venueId == offerers_models.Venue.id,
                )
                .correlate(offerers_models.Venue)
                .is_(False)
            ),
        },
    },
    "OFFERER_TAG": {
        "field": "offerer_tags",
        "column": offerers_models.OffererTagMapping.tagId,
        "inner_join": "offerer_tag_mapping",
        "custom_filters_inner_joins": {
            "NOT_IN": ["offerer"],
            "NOT_EXIST": ["offerer"],
        },
        "custom_filters": {
            "NOT_IN": lambda values: (
                sa.exists()
                .where(
                    sa.and_(
                        offerers_models.OffererTagMapping.offererId == offerers_models.Offerer.id,
                        offerers_models.OffererTagMapping.tagId.in_(values),
                    )
                )
                .correlate(offerers_models.Offerer)
                .is_(False)
            ),
            "NOT_EXIST": lambda values: (
                sa.exists()
                .where(
                    offerers_models.OffererTagMapping.offererId == offerers_models.Offerer.id,
                )
                .correlate(offerers_models.Offerer)
                .is_(False)
            ),
        },
    },
    "STATUS": {
        "field": "status",
        "column": offers_models.Offer.status,
    },
    "SUBCATEGORY": {
        "field": "subcategory",
        "facet": "offer.subcategoryId",
        "llm_filter": "offer_subcategory_id",
        "column": offers_models.Offer.subcategoryId,
    },
    "SYNCHRONIZED": {
        "field": "boolean",
        "special": lambda x: x != "true",
        "column": offers_models.Offer.idAtProvider,
    },
    "HEADLINE": {
        "field": "boolean",
        "special": lambda x: x == "true",
        "column": offers_models.Offer.is_headline_offer,
    },
    "HIGHLIGHT_REQUEST": {
        "field": "highlight",
        "column": highlights_models.HighlightRequest.highlightId,
        "inner_join": "highlight_request",
    },
    "PROVIDER": {
        "field": "provider",
        "column": offers_models.Offer.lastProviderId,
    },
    "VENUE": {
        "field": "venue",
        "facet": "venue.id",
        "column": offers_models.Offer.venueId,
    },
    "VENUE_TYPE": {
        "field": "venue_type",
        "column": offerers_models.Venue.venueTypeCode,
        "inner_join": "venue",
    },
    "VALIDATED_OFFERER": {
        "field": "boolean",
        "special": lambda x: x == "true",
        "column": offerers_models.Offerer.isValidated,
        "inner_join": "offerer",
    },
    "VALIDATION": {
        "field": "validation",
        "column": offers_models.Offer.validation,
    },
    "PRICE": {
        "field": "price",
        "column": offers_models.Stock.price,
        "llm_filter": "last_stock_price",
        "llm_special": lambda p: float(p),
        "facet": "offer.prices",
        "subquery_join": "stock",
        "custom_filter_all_operators": sa.and_(
            offers_models.Stock._bookable,
            offers_models.Offer._released,
        ),
    },
    "MEDIATION": {
        "field": "boolean",
        "special": lambda x: x == "true",
        "custom_filters": {
            "NULLABLE": lambda value: (
                sa.exists()
                .where(
                    sa.and_(
                        offers_models.Mediation.offerId == offers_models.Offer.id,
                        offers_models.Mediation.isActive.is_(True),
                    )
                )
                .is_(value)
            )
        },
    },
    "ALLOCINE_ID": {
        "field": "integer",
        "inner_join": "product",
        "special": str,
        "column": offers_models.Product.extraData.op("->")("allocineId"),  # use the index
    },
    "SHOW_TYPE": {
        "facet": "offer.showType",
        "field": "show_type",
    },
}

JOIN_DICT: dict[str, list[dict[str, typing.Any]]] = {
    "product": [
        {
            "name": "product",
            "args": (offers_models.Product, offers_models.Offer.product),
        },
    ],
    "criterion": [
        {
            "name": "criterion",
            "args": (criteria_models.Criterion, offers_models.Offer.criteria),
        },
    ],
    "offer_criterion": [
        {
            "name": "offer_criterion",
            "args": (criteria_models.OfferCriterion, offers_models.Offer.id == criteria_models.OfferCriterion.offerId),
        },
    ],
    "offerer_address": [
        {
            "name": "offerer_address",
            "args": (offerers_models.OffererAddress, offers_models.Offer.offererAddress),
        },
    ],
    "address": [
        {
            "name": "offerer_address",
            "args": (offerers_models.OffererAddress, offers_models.Offer.offererAddress),
        },
        {
            "name": "address",
            "args": (geography_models.Address, offerers_models.OffererAddress.address),
        },
    ],
    "venue": [
        {
            "name": "venue",
            "args": (offerers_models.Venue, offers_models.Offer.venue),
        },
    ],
    "highlight_request": [
        {
            "name": "highlight_request",
            "args": (
                highlights_models.HighlightRequest,
                highlights_models.HighlightRequest.offerId == offers_models.Offer.id,
            ),
        },
    ],
    "offerer": [
        {
            "name": "venue",
            "args": (offerers_models.Venue, offers_models.Offer.venue),
        },
        {
            "name": "offerer",
            "args": (offerers_models.Offerer, offerers_models.Venue.managingOfferer),
        },
    ],
    "offerer_tag_mapping": [
        {
            "name": "venue",
            "args": (offerers_models.Venue, offers_models.Offer.venue),
        },
        {
            "name": "offerer",
            "args": (offerers_models.Offerer, offerers_models.Venue.managingOfferer),
        },
        {
            "name": "offerer_tag_mapping",
            "args": (
                offerers_models.OffererTagMapping,
                offerers_models.OffererTagMapping.offererId == offerers_models.Offerer.id,
            ),
        },
    ],
    "venue_criterion": [
        {
            "name": "venue",
            "args": (offerers_models.Venue, offers_models.Offer.venue),
        },
        {
            "name": "venue_criterion",
            "args": (
                offerers_models.VenueCriterion,
                offerers_models.VenueCriterion.venueId == offerers_models.Venue.id,
            ),
        },
    ],
}

SUBQUERY_DICT: dict[str, dict[str, typing.Any]] = {
    "stock": {
        "name": "stock",
        "table": offers_models.Stock,
        "constraint": sa.and_(
            offers_models.Stock.offerId == offers_models.Offer.id,
            offers_models.Stock.isSoftDeleted.is_(False),
        ),
    },
}


class OfferDetailsActionType(enum.StrEnum):
    ACTIVATE = enum.auto()
    DEACTIVATE = enum.auto()
    VALIDATE = enum.auto()
    PENDING = enum.auto()
    REJECT = enum.auto()
    TAG_WEIGHT = enum.auto()
    RESYNC = enum.auto()
    EDIT_VENUE = enum.auto()


@dataclasses.dataclass
class OfferDetailsAction:
    type: OfferDetailsActionType
    position: int
    inline: bool


class OfferDetailsActions:
    def __init__(self, threshold: int) -> None:
        self.current_pos = 0
        self.actions: list[OfferDetailsAction] = []
        self.threshold = threshold

    def add_action(self, action_type: OfferDetailsActionType) -> None:
        self.actions.append(
            OfferDetailsAction(type=action_type, position=self.current_pos, inline=self.current_pos < self.threshold)
        )
        self.current_pos += 1

    def __contains__(self, action_type: OfferDetailsActionType) -> bool:
        return action_type in [e.type for e in self.actions]

    @property
    def inline_actions(self) -> list[OfferDetailsActionType]:
        return [action.type for action in self.actions if action.inline]

    @property
    def additional_actions(self) -> list[OfferDetailsActionType]:
        return [action.type for action in self.actions if not action.inline]


def _get_offer_ids_algolia(form: forms.GetOfferAlgoliaSearchForm) -> list[int]:
    filters, warnings = utils.generate_algolia_search_string(
        search_parameters=form.search.data,
        fields_definition=SEARCH_FIELD_TO_PYTHON,
    )
    for warning in warnings:
        flash(escape(warning), "warning")

    # +1 to check if there are more results than requested
    ids = search_offer_ids(query=form.algolia_search.data or "", count=form.limit.data + 1, **filters)
    return ids


def _get_offer_ids_query(form: forms.GetOfferAdvancedSearchForm) -> sa_orm.Query:
    query, _, _, warnings = utils.generate_search_query(
        query=db.session.query(offers_models.Offer),
        search_parameters=form.search.data,
        fields_definition=SEARCH_FIELD_TO_PYTHON,
        joins_definition=JOIN_DICT,
        subqueries_definition=SUBQUERY_DICT,
    )
    for warning in warnings:
        flash(escape(warning), "warning")

    # +1 to check if there are more results than requested
    # union() above may cause duplicates, but distinct() affects performance and causes timeout;
    # actually duplicate ids can be accepted since the current function is called inside .in_()
    return query.with_entities(offers_models.Offer.id).limit(form.limit.data + 1)


def _get_offers_by_ids(
    offer_ids: list[int] | sa_orm.Query, *, sort: str | None = None, order: str | None = None
) -> list[sa.engine.Row]:
    if utils.has_current_user_permission(perm_models.Permissions.PRO_FRAUD_ACTIONS):
        # Those columns are not shown to fraud pro users
        booked_quantity_subquery: sa.sql.selectable.ScalarSelect | sa.sql.elements.Null = sa.null()
        remaining_quantity_case: sa.sql.elements.Case | sa.sql.elements.Null = sa.null()

        # Aggregate validation rules as an array of names returned in a single row
        rules_subquery: sa.sql.selectable.ScalarSelect | sa.sql.elements.Null = (
            sa.select(sa.func.array_agg(offers_models.OfferValidationRule.name))
            .select_from(offers_models.OfferValidationRule)
            .join(offers_models.ValidationRuleOfferLink)
            .filter(offers_models.ValidationRuleOfferLink.offerId == offers_models.Offer.id)
            .correlate(offers_models.Offer)
            .scalar_subquery()
        )

        # build an object which can be read by jinja macro as if it was the Offerer
        aliased_offerer = sa_orm.aliased(offerers_models.Offerer)
        offerer_badges_subquery: sa.sql.selectable.ScalarSelect | sa.sql.elements.Null = (
            sa.select(
                sa.func.jsonb_build_object(
                    "confidenceLevel",
                    offerers_models.OffererConfidenceRule.confidenceLevel,
                    "isTopActeur",
                    aliased_offerer.is_top_acteur,
                )
            )
            .select_from(aliased_offerer)
            .outerjoin(offerers_models.OffererConfidenceRule)
            .filter(aliased_offerer.id == offerers_models.Offerer.id)
            .correlate(offerers_models.Offerer)
            .scalar_subquery()
        )

        # build an object which can be read by jinja macro as if it was the Venue
        venue_badges_subquery: sa.sql.selectable.ScalarSelect | sa.sql.elements.Null = (
            sa.select(
                sa.func.jsonb_build_object("confidenceLevel", offerers_models.OffererConfidenceRule.confidenceLevel)
            )
            .select_from(offerers_models.OffererConfidenceRule)
            .filter(offerers_models.OffererConfidenceRule.venueId == offerers_models.Venue.id)
            .correlate(offerers_models.Venue)
            .scalar_subquery()
        )

    else:
        # Compute displayed information in remaining stock column directly, don't joinedload/fetch huge stock data
        booked_quantity_subquery = (
            sa.select(sa.func.coalesce(sa.func.sum(offers_models.Stock.dnBookedQuantity), 0))
            .select_from(offers_models.Stock)
            .filter(offers_models.Stock.offerId == offers_models.Offer.id)
            .correlate(offers_models.Offer)
            .scalar_subquery()
        )

        remaining_quantity_case = sa.case(
            (
                # Same as Offer.isReleased which is not an hybrid property
                sa.and_(
                    offers_models.Offer._released,
                    offerers_models.Offerer.isActive,
                    offerers_models.Offerer.isValidated,
                ),
                (
                    sa.select(
                        sa.case(
                            (
                                sa.func.coalesce(
                                    sa.func.max(sa.case((offers_models.Stock.remainingStock.is_(None), 1), else_=0)),
                                    0,
                                )
                                == 0,
                                sa.func.coalesce(sa.func.sum(offers_models.Stock.remainingStock), 0).cast(sa.String),
                            ),
                            else_="Illimité",
                        )
                    )
                    .select_from(offers_models.Stock)
                    .filter(offers_models.Stock.offerId == offers_models.Offer.id)
                    .correlate(offers_models.Offer)
                    .scalar_subquery()
                ),
            ),
            else_="-",
        )

        # Those columns are not shown to non fraud pro users
        rules_subquery = sa.null()
        offerer_badges_subquery = sa.null()
        venue_badges_subquery = sa.null()

    # Aggregate min and max prices as dict returned in a single row
    min_max_prices_subquery: sa.sql.selectable.ScalarSelect | sa.sql.elements.Null = (
        sa.select(
            sa.func.jsonb_build_object(
                "min_price",
                sa.func.min(sa.func.coalesce(offers_models.PriceCategory.price, offers_models.Stock.price)),
                "max_price",
                sa.func.max(sa.func.coalesce(offers_models.PriceCategory.price, offers_models.Stock.price)),
            )
        )
        .select_from(offers_models.Stock)
        .outerjoin(offers_models.Stock.priceCategory)
        .filter(offers_models.Stock.offerId == offers_models.Offer.id, ~offers_models.Stock.isSoftDeleted)
        .correlate(offers_models.Offer)
        .scalar_subquery()
    )

    # retrieve one product mediation
    product_mediation_uuid_subquery = (
        sa.select(offers_models.ProductMediation.uuid)
        .select_from(offers_models.ProductMediation)
        .filter(offers_models.ProductMediation.productId == offers_models.Offer.productId)
        .order_by(offers_models.ProductMediation.imageType)  # retrieves the RECTO first
        .correlate(offers_models.Offer)
        .limit(1)
        .scalar_subquery()
    )

    offer_mediation_subquery = (
        sa.select(
            sa.func.jsonb_build_object(
                "id",
                offers_models.Mediation.id,
                "thumbCount",
                offers_models.Mediation.thumbCount,
            )
        )
        .select_from(offers_models.Mediation)
        .filter(
            offers_models.Mediation.isActive.is_(True),
            offers_models.Mediation.offerId == offers_models.Offer.id,
        )
        .order_by(offers_models.Mediation.dateCreated.desc())  # only takes the last one
        .correlate(offers_models.Offer)
        .limit(1)
        .scalar_subquery()
    )

    offer_event_datetimes = (
        sa.select(
            sa.case(
                (
                    sa.or_(
                        sa.not_(offers_models.Offer.isEvent),
                        sa.func.max(offers_models.Stock.beginningDatetime).is_(None),
                    ),
                    sa.cast(postgresql.array([]), postgresql.ARRAY(sa.DateTime)),
                ),
                (
                    sa.func.max(offers_models.Stock.beginningDatetime)
                    == sa.func.min(offers_models.Stock.beginningDatetime),
                    postgresql.array([sa.func.max(offers_models.Stock.beginningDatetime)]),
                ),
                else_=postgresql.array(
                    [
                        sa.func.min(offers_models.Stock.beginningDatetime),
                        sa.func.max(offers_models.Stock.beginningDatetime),
                    ]
                ),
            )
        )
        .select_from(offers_models.Stock)
        .filter(offers_models.Stock.offerId == offers_models.Offer.id)
        .correlate(offers_models.Offer)
        .scalar_subquery()
    )

    offer_booking_limit_datetimes = (
        sa.select(
            sa.case(
                (
                    sa.or_(
                        sa.not_(offers_models.Offer.isEvent),
                        sa.func.max(offers_models.Stock.bookingLimitDatetime).is_(None),
                    ),
                    sa.cast(postgresql.array([]), postgresql.ARRAY(sa.DateTime)),
                ),
                (
                    sa.func.max(offers_models.Stock.bookingLimitDatetime)
                    == sa.func.min(offers_models.Stock.bookingLimitDatetime),
                    postgresql.array([sa.func.max(offers_models.Stock.bookingLimitDatetime)]),
                ),
                else_=postgresql.array(
                    [
                        sa.func.min(offers_models.Stock.bookingLimitDatetime),
                        sa.func.max(offers_models.Stock.bookingLimitDatetime),
                    ]
                ),
            )
        )
        .select_from(offers_models.Stock)
        .filter(
            offers_models.Stock.offerId == offers_models.Offer.id,
            offers_models.Stock.bookingLimitDatetime >= date_utils.get_naive_utc_now(),
        )
        .correlate(offers_models.Offer)
        .scalar_subquery()
    )

    # Aggregate tags as an array of names returned in a single row (joinedload would fetch 1 result row per tag)
    tags_subquery = (
        (
            sa.select(sa.func.array_agg(criteria_models.Criterion.name))
            .select_from(criteria_models.Criterion)
            .join(criteria_models.OfferCriterion)
            .filter(criteria_models.OfferCriterion.offerId == offers_models.Offer.id)
            .correlate(offers_models.Offer)
            .scalar_subquery()
        )
        if utils.has_current_user_permission(perm_models.Permissions.MANAGE_OFFERS_AND_VENUES_TAGS)
        else sa.null()
    )

    query = (
        db.session.query(
            offers_models.Offer,
            booked_quantity_subquery.label("booked_quantity"),
            remaining_quantity_case.label("remaining_quantity"),
            offer_event_datetimes.label("offer_event_datetimes"),
            offer_booking_limit_datetimes.label("offer_booking_limit_datetimes"),
            tags_subquery.label("tags"),
            rules_subquery.label("rules"),
            offerer_badges_subquery.label("offerer_badges"),
            venue_badges_subquery.label("venue_badges"),
            min_max_prices_subquery.label("prices"),
            offer_mediation_subquery.label("offer_mediation"),
            product_mediation_uuid_subquery.label("product_mediation"),
        )
        .filter(offers_models.Offer.id.in_(offer_ids))
        # 1-1 relationships so join will not increase the number of SQL rows
        .join(offers_models.Offer.venue)
        .join(offerers_models.Venue.managingOfferer)
        .options(
            sa_orm.load_only(
                offers_models.Offer.id,
                offers_models.Offer.name,
                offers_models.Offer.subcategoryId,
                offers_models.Offer.rankingWeight,
                offers_models.Offer.dateCreated,
                offers_models.Offer.validation,
                offers_models.Offer.lastValidationDate,
                offers_models.Offer.lastValidationType,
                offers_models.Offer.publicationDatetime,
                offers_models.Offer._extraData,
                offers_models.Offer.lastProviderId,
                offers_models.Offer.ean,
                offers_models.Offer.offererAddressId,
            ),
            sa_orm.contains_eager(offers_models.Offer.venue).options(
                sa_orm.load_only(
                    offerers_models.Venue.id,
                    offerers_models.Venue.isSoftDeleted,
                    offerers_models.Venue.name,
                    offerers_models.Venue.publicName,
                    offerers_models.Venue.siret,
                ),
                sa_orm.contains_eager(offerers_models.Venue.managingOfferer).options(
                    sa_orm.load_only(
                        offerers_models.Offerer.id,
                        offerers_models.Offerer.name,
                    ),
                ),
                sa_orm.selectinload(offerers_models.Venue.offererAddress)
                .load_only()
                .joinedload(offerers_models.OffererAddress.address)
                .load_only(geography_models.Address.departmentCode),
            ),
            sa_orm.joinedload(offers_models.Offer.author).load_only(
                users_models.User.id,
                users_models.User.firstName,
                users_models.User.lastName,
            ),
            sa_orm.joinedload(offers_models.Offer.compliance),
            sa_orm.selectinload(offers_models.Offer.lastProvider).load_only(
                providers_models.Provider.name,
            ),
            sa_orm.selectinload(offers_models.Offer.offererAddress)
            .load_only()
            .joinedload(offerers_models.OffererAddress.address)
            .load_only(
                geography_models.Address.departmentCode,
                geography_models.Address.timezone,
            ),
            sa_orm.joinedload(offers_models.Offer.product).load_only(
                offers_models.Product.ean,
                offers_models.Product.extraData,
            ),
        )
    )

    if sort:
        order = order or "desc"
        query = query.order_by(getattr(getattr(offers_models.Offer, sort), order)())

    return query.all()


def _render_offer_list(
    rows: list | None = None,
    advanced_form: forms.GetOfferAdvancedSearchForm | None = None,
    algolia_form: forms.GetOfferAlgoliaSearchForm | None = None,
    llm_form: forms.GetOfferLlmSearchForm | None = None,
    code: int = 200,
    page: str = "offer",
    is_form_empty: bool = False,
    **kwargs: dict,
) -> utils.BackofficeResponse:
    date_created_sort_url = None
    if advanced_form is not None and advanced_form.sort.data:
        date_created_sort_url = advanced_form.get_sort_link_with_search_data(".list_offers")

    if not advanced_form:
        advanced_form = forms.GetOfferAdvancedSearchForm(
            formdata=MultiDict(
                (
                    ("search-0-search_field", "ID"),
                    ("search-0-operator", "IN"),
                ),
            ),
        )

    connect_as = {}
    for row in rows or []:
        offer = row.Offer
        connect_as[offer.id] = get_connect_as(
            object_type="offer",
            object_id=offer.id,
            pc_pro_path=urls.build_pc_pro_offer_path(offer),
        )

    return (
        render_template(
            "offer/list.html",
            rows=rows or [],
            advanced_form=advanced_form,
            advanced_dst=url_for(".list_offers"),
            algolia_form=algolia_form or forms.GetOfferAlgoliaSearchForm(),
            algolia_dst=url_for(".list_algolia_offers"),
            llm_form=llm_form or forms.GetOfferLlmSearchForm(),
            llm_dst=url_for(".list_llm_offers"),
            date_created_sort_url=date_created_sort_url,
            connect_as=connect_as,
            page=page,
            is_form_empty=is_form_empty,
            **kwargs,
        ),
        code,
    )


@list_offers_blueprint.route("", methods=["GET"])
def list_offers() -> utils.BackofficeResponse:
    form = forms.GetOfferAdvancedSearchForm(formdata=utils.get_query_params())
    if not form.validate():
        mark_transaction_as_invalid()
        return _render_offer_list(
            advanced_form=form,
            code=400,
            page="offer",
            is_form_empty=True,
        )

    if form.is_empty():
        form_data = MultiDict(utils.get_query_params())
        form_data.update({"search-0-search_field": "ID", "search-0-operator": "IN"})
        form = forms.GetOfferAdvancedSearchForm(formdata=form_data)
        return _render_offer_list(advanced_form=form, page="offer", is_form_empty=True)

    offers = _get_offers_by_ids(
        offer_ids=_get_offer_ids_query(form),
        sort=form.sort.data,
        order=form.order.data,
    )
    offers = utils.limit_rows(offers, form.limit.data)

    return _render_offer_list(
        rows=offers,
        advanced_form=form,
        page="offer",
        is_form_empty=False,
    )


@list_offers_blueprint.route("/algolia", methods=["GET"])
def list_algolia_offers() -> utils.BackofficeResponse:
    form = forms.GetOfferAlgoliaSearchForm(formdata=utils.get_query_params())
    if not form.validate():
        mark_transaction_as_invalid()
        return _render_offer_list(
            algolia_form=form,
            code=400,
            page="algolia",
            is_form_empty=True,
        )

    offer_ids = _get_offer_ids_algolia(form)
    offers = []
    if offer_ids:
        offers = _get_offers_by_ids(
            offer_ids=offer_ids,
            sort=form.sort.data,
            order=form.order.data,
        )
        offers = utils.limit_rows(offers, form.limit.data)

    return _render_offer_list(
        rows=offers,
        algolia_form=form,
        page="algolia",
        is_form_empty=form.is_empty(),
    )


@list_offers_blueprint.route("/llm", methods=["GET"])
def list_llm_offers() -> utils.BackofficeResponse:
    form = forms.GetOfferLlmSearchForm(formdata=utils.get_query_params())
    is_form_empty = True
    if not form.validate():
        mark_transaction_as_invalid()
        return _render_offer_list(
            llm_form=form,
            code=400,
            page="llm",
            is_form_empty=is_form_empty,
        )

    filters, warnings = utils.generate_llm_search_dict(
        search_parameters=form.search.data,
        fields_definition=SEARCH_FIELD_TO_PYTHON,
    )
    for warning in warnings:
        flash(escape(warning), "warning")

    try:
        responses = compliance_backend.search_offers(
            payload=SearchOffersRequest(query=form.llm_search.data, filters=filters)
        )
        is_form_empty = False
    except ExternalAPIException as e:
        flash(
            f"Le chatbot a rencontré un problème{', veuillez reéssayer plus tard' if e.is_retryable else ''}", "warning"
        )
        responses = None

    offers_pertinence = {o.offer_id: o.pertinence for o in responses.results} if responses else {}

    offers = []
    if offers_pertinence:
        offers = _get_offers_by_ids(
            offer_ids=list(offers_pertinence),
            sort=form.sort.data,
            order=form.order.data,
        )
        offers = utils.limit_rows(offers, form.limit.data)

    return _render_offer_list(
        rows=offers,
        llm_form=form,
        page="llm",
        offers_pertinence=offers_pertinence,
        is_form_empty=(form.is_empty() or is_form_empty),
    )


@list_offers_blueprint.route("/<int:offer_id>/edit", methods=["GET"])
@utils.permission_required(perm_models.Permissions.MANAGE_OFFERS)
def get_edit_offer_form(offer_id: int) -> utils.BackofficeResponse:
    offer = (
        db.session.query(offers_models.Offer)
        .filter_by(id=offer_id)
        .options(
            sa_orm.joinedload(offers_models.Offer.criteria).load_only(
                criteria_models.Criterion.id, criteria_models.Criterion.name
            )
        )
        .one_or_none()
    )
    if not offer:
        raise NotFound()

    form = forms.EditOfferForm(utils.get_query_params())
    form.criteria.choices = [(criterion.id, criterion.name) for criterion in offer.criteria]
    if offer.rankingWeight:
        form.rankingWeight.data = offer.rankingWeight

    return render_template(
        "components/dynamic/modal_form.html",
        target_id=f"#offer-row-{offer_id}",
        form=form,
        dst=url_for("backoffice_web.offer.edit_offer", offer_id=offer.id),
        div_id=f"edit-offer-modal-{offer.id}",
        title=f"Édition de l'offre {offer.name}",
        button_text="Enregistrer les modifications",
        ajax_submit=not form.redirect.data,
    )


@list_offers_blueprint.route("/batch/validate", methods=["POST"])
@utils.permission_required(perm_models.Permissions.PRO_FRAUD_ACTIONS)
def get_batch_validate_offers_form() -> utils.BackofficeResponse:
    form = empty_forms.BatchForm()
    return render_template(
        "components/dynamic/modal_form.html",
        target_id="#offers-table",
        form=form,
        dst=url_for("backoffice_web.offer.batch_validate_offers"),
        div_id="batch-validate-offer-modal",
        title="Voulez-vous valider les offres sélectionnées ?",
        button_text="Valider",
    )


@list_offers_blueprint.route("/batch-validate", methods=["POST"])
@utils.permission_required(perm_models.Permissions.PRO_FRAUD_ACTIONS)
def batch_validate_offers() -> utils.BackofficeResponse:
    form = empty_forms.BatchForm()
    if not form.validate():
        mark_transaction_as_invalid()
        flash(utils.build_form_error_msg(form), "warning")
        return redirect(request.referrer, 400)

    _batch_validate_offers(form.object_ids_list)
    flash("Les offres ont été validées", "success")
    return _render_offer_rows(form.object_ids_list)


@list_offers_blueprint.route("/batch/pending", methods=["POST"])
@utils.permission_required(perm_models.Permissions.PRO_FRAUD_ACTIONS)
def get_batch_pending_offers_form() -> utils.BackofficeResponse:
    form = empty_forms.BatchForm()
    return render_template(
        "components/dynamic/modal_form.html",
        target_id="#offers-table",
        form=form,
        dst=url_for("backoffice_web.offer.batch_pending_offers"),
        div_id="batch-pending-offer-modal",
        title="Voulez-vous annuler la validation des offres sélectionnées ?",
        information="Les offres repasseront en instruction et ne seront plus réservables. Les réservations en cours ne seront pas annulées.",
        button_text="Repasser en instruction",
    )


@list_offers_blueprint.route("/batch-pending", methods=["POST"])
@utils.permission_required(perm_models.Permissions.PRO_FRAUD_ACTIONS)
def batch_pending_offers() -> utils.BackofficeResponse:
    form = empty_forms.BatchForm()
    if not form.validate():
        mark_transaction_as_invalid()
        flash(utils.build_form_error_msg(form), "warning")
        return redirect(request.referrer, 400)

    _batch_pending_offers(form.object_ids_list)
    flash(
        "Les offres sont repassées en instruction et ne sont plus réservables. Les réservations en cours ne sont pas annulées.",
        "success",
    )
    return _render_offer_rows(form.object_ids_list)


@list_offers_blueprint.route("/batch/reject", methods=["POST"])
@utils.permission_required(perm_models.Permissions.PRO_FRAUD_ACTIONS)
def get_batch_reject_offers_form() -> utils.BackofficeResponse:
    form = empty_forms.BatchForm()
    return render_template(
        "components/dynamic/modal_form.html",
        target_id="#offers-table",
        form=form,
        dst=url_for("backoffice_web.offer.batch_reject_offers"),
        div_id="batch-reject-offer-modal",
        title="Voulez-vous rejeter les offres sélectionnées ?",
        button_text="Rejeter",
    )


@list_offers_blueprint.route("/batch-reject", methods=["POST"])
@utils.permission_required(perm_models.Permissions.PRO_FRAUD_ACTIONS)
def batch_reject_offers() -> utils.BackofficeResponse:
    form = empty_forms.BatchForm()
    if not form.validate():
        mark_transaction_as_invalid()
        flash(utils.build_form_error_msg(form), "warning")
        return redirect(request.referrer, 400)

    _batch_reject_offers(form.object_ids_list)
    flash("Les offres ont été rejetées", "success")
    return _render_offer_rows(form.object_ids_list)


@list_offers_blueprint.route("/batch/edit", methods=["POST"])
@utils.permission_required(perm_models.Permissions.MANAGE_OFFERS)
def get_batch_edit_offer_form() -> utils.BackofficeResponse:
    form = forms.BatchEditOfferForm()
    if form.object_ids.data:
        if not form.validate():
            mark_transaction_as_invalid()
            flash(utils.build_form_error_msg(form), "warning")
            return redirect(request.referrer, 400)

        offers = (
            db.session.query(offers_models.Offer)
            .filter(offers_models.Offer.id.in_(form.object_ids_list))
            .options(
                sa_orm.joinedload(offers_models.Offer.criteria).load_only(
                    criteria_models.Criterion.id, criteria_models.Criterion.name
                )
            )
            .all()
        )
        criteria = set.intersection(*[set(offer.criteria) for offer in offers])

        if len(criteria) > 0:
            form.criteria.choices = [(criterion.id, criterion.name) for criterion in criteria]

    return render_template(
        "components/dynamic/modal_form.html",
        target_id="#offers-table",
        form=form,
        dst=url_for("backoffice_web.offer.batch_edit_offer"),
        div_id="batch-edit-offer-modal",
        title="Édition des offres",
        button_text="Enregistrer les modifications",
    )


@list_offers_blueprint.route("/batch-edit", methods=["POST"])
@utils.permission_required(perm_models.Permissions.MANAGE_OFFERS)
def batch_edit_offer() -> utils.BackofficeResponse:
    form = forms.BatchEditOfferForm()
    if not form.validate():
        mark_transaction_as_invalid()
        flash(utils.build_form_error_msg(form), "warning")
        return redirect(request.referrer, 400)

    offers = (
        db.session.query(offers_models.Offer)
        .filter(offers_models.Offer.id.in_(form.object_ids_list))
        .options(sa_orm.joinedload(offers_models.Offer.criteria))
        .all()
    )
    criteria = (
        db.session.query(criteria_models.Criterion).filter(criteria_models.Criterion.id.in_(form.criteria.data)).all()
    )

    previous_criteria = set.intersection(*[set(offer.criteria) for offer in offers])
    deleted_criteria = previous_criteria.difference(criteria)

    for offer in offers:
        if offer.criteria:
            offer.criteria.extend(criterion for criterion in criteria if criterion not in offer.criteria)
            for criterion in deleted_criteria:
                offer.criteria.remove(criterion)
        else:
            offer.criteria = criteria

        if form.rankingWeight.data == 0:
            offer.rankingWeight = None
        elif form.rankingWeight.data:
            offer.rankingWeight = form.rankingWeight.data

        db.session.add(offer)

    db.session.flush()

    on_commit(
        functools.partial(
            search.async_index_offer_ids,
            form.object_ids_list,
            reason=IndexationReason.OFFER_BATCH_UPDATE,
        )
    )

    flash("Les offres ont été modifiées", "success")
    return _render_offer_rows(form.object_ids_list)


@list_offers_blueprint.route("/<int:offer_id>/edit", methods=["POST"])
@utils.permission_required(perm_models.Permissions.MANAGE_OFFERS)
def edit_offer(offer_id: int) -> utils.BackofficeResponse:
    offer = db.session.query(offers_models.Offer).filter_by(id=offer_id).one_or_none()
    if not offer:
        raise NotFound()

    form = forms.EditOfferForm()

    if not form.validate():
        mark_transaction_as_invalid()
        flash("Le formulaire n'est pas valide", "warning")
        return redirect(request.referrer, 400)

    criteria = (
        db.session.query(criteria_models.Criterion).filter(criteria_models.Criterion.id.in_(form.criteria.data)).all()
    )

    offer.criteria = criteria
    offer.rankingWeight = form.rankingWeight.data
    db.session.add(offer)
    db.session.flush()

    #  Immediately index offer if tags are updated: tags are used by
    #  other tools (eg. building playlists for the home page) and
    #  waiting N minutes for the next indexing cron tasks is painful.
    on_commit(functools.partial(search.reindex_offer_ids, [offer.id]))

    flash("L'offre a été modifiée", "success")

    if utils.is_request_from_htmx():
        return _render_offer_rows([offer_id])

    return redirect(request.referrer or url_for("backoffice_web.offer.list_offers"), 303)


@list_offers_blueprint.route("/<int:offer_id>/validate", methods=["GET"])
@utils.permission_required(perm_models.Permissions.PRO_FRAUD_ACTIONS)
def get_validate_offer_form(offer_id: int) -> utils.BackofficeResponse:
    offer = db.session.query(offers_models.Offer).filter_by(id=offer_id).one_or_none()

    if not offer:
        raise NotFound()

    form = empty_forms.DynamicForm(utils.get_query_params())

    return render_template(
        "components/dynamic/modal_form.html",
        target_id=f"#offer-row-{offer_id}",
        form=form,
        dst=url_for("backoffice_web.offer.validate_offer", offer_id=offer.id),
        div_id=f"validate-offer-modal-{offer.id}",
        title=f"Validation de l'offre {offer.name}",
        button_text="Valider l'offre",
        ajax_submit=not form.redirect.data,
    )


def _render_offer_rows(offer_ids: list[int]) -> utils.BackofficeResponse:
    offer_rows = _get_offers_by_ids(offer_ids=offer_ids)
    connect_as = {}
    for offer_row in offer_rows:
        offer = offer_row.Offer
        connect_as[offer.id] = get_connect_as(
            object_type="offer",
            object_id=offer.id,
            pc_pro_path=urls.build_pc_pro_offer_path(offer),
        )
    return render_template(
        "offer/list_rows.html",
        rows=offer_rows,
        connect_as=connect_as,
    )


@list_offers_blueprint.route("/<int:offer_id>/validate", methods=["POST"])
@utils.permission_required(perm_models.Permissions.PRO_FRAUD_ACTIONS)
def validate_offer(offer_id: int) -> utils.BackofficeResponse:
    _batch_validate_offers([offer_id])
    flash("L'offre a été validée", "success")

    if utils.is_request_from_htmx():
        return _render_offer_rows([offer_id])
    return redirect(request.referrer or url_for("backoffice_web.offer.list_offers"), 303)


@list_offers_blueprint.route("/<int:offer_id>/pending", methods=["GET"])
@utils.permission_required(perm_models.Permissions.PRO_FRAUD_ACTIONS)
def get_pending_offer_form(offer_id: int) -> utils.BackofficeResponse:
    offer = db.session.query(offers_models.Offer).filter_by(id=offer_id).one_or_none()

    if not offer:
        raise NotFound()

    form = empty_forms.DynamicForm(utils.get_query_params())

    return render_template(
        "components/dynamic/modal_form.html",
        target_id=f"#offer-row-{offer_id}",
        form=form,
        dst=url_for("backoffice_web.offer.pending_offer", offer_id=offer.id),
        div_id=f"pending-offer-modal-{offer.id}",
        title=f"Annuler la validation de l'offre {offer.name}",
        information="L’offre repassera en instruction et ne sera plus réservable. Les réservations en cours ne seront pas annulées.",
        button_text="Repasser en instruction",
        ajax_submit=not form.redirect.data,
    )


@list_offers_blueprint.route("/<int:offer_id>/pending", methods=["POST"])
@utils.permission_required(perm_models.Permissions.PRO_FRAUD_ACTIONS)
def pending_offer(offer_id: int) -> utils.BackofficeResponse:
    _batch_pending_offers([offer_id])
    flash(
        "L’offre est repassée en instruction et n'est plus réservable. Les réservations en cours ne sont pas annulées",
        "success",
    )

    if utils.is_request_from_htmx():
        return _render_offer_rows([offer_id])
    return redirect(request.referrer or url_for("backoffice_web.offer.list_offers"), 303)


@list_offers_blueprint.route("/<int:offer_id>/reject", methods=["GET"])
@utils.permission_required(perm_models.Permissions.PRO_FRAUD_ACTIONS)
def get_reject_offer_form(offer_id: int) -> utils.BackofficeResponse:
    offer = db.session.query(offers_models.Offer).filter_by(id=offer_id).one_or_none()

    if not offer:
        raise NotFound()

    form = empty_forms.DynamicForm(formdata=utils.get_query_params())

    return render_template(
        "components/dynamic/modal_form.html",
        target_id=f"#offer-row-{offer_id}",
        form=form,
        dst=url_for("backoffice_web.offer.reject_offer", offer_id=offer.id),
        div_id=f"reject-offer-modal-{offer.id}",
        title=f"Rejet de l'offre {offer.name}",
        button_text="Rejeter l'offre",
        ajax_submit=not form.redirect.data,
    )


@list_offers_blueprint.route("/<int:offer_id>/reject", methods=["POST"])
@utils.permission_required(perm_models.Permissions.PRO_FRAUD_ACTIONS)
def reject_offer(offer_id: int) -> utils.BackofficeResponse:
    _batch_reject_offers([offer_id])
    flash("L'offre a été rejetée", "success")

    if utils.is_request_from_htmx():
        return _render_offer_rows([offer_id])
    return redirect(request.referrer or url_for("backoffice_web.offer.list_offers"), 303)


def _get_offer_recipients(offer: offers_models.Offer) -> list[str]:
    if offer.venue.bookingEmail:
        return [offer.venue.bookingEmail]

    # Additional query in a loop is acceptable here since we rarely have no venue.bookingEmail
    user_offerer_emails = (
        db.session.query(users_models.User.email)
        .join(users_models.User.UserOfferers)
        .filter(
            offerers_models.UserOfferer.offererId == offer.venue.managingOffererId,
            offerers_models.UserOfferer.isValidated,
        )
        .all()
    )
    return [email for (email,) in user_offerer_emails]


def _batch_validate_offers(offer_ids: list[int]) -> None:
    new_validation = offers_models.OfferValidationStatus.APPROVED

    aliased_venue = sa_orm.aliased(offerers_models.Venue)

    max_price_subquery = (
        sa.select(sa.func.max(offers_models.Stock.price))
        .select_from(offers_models.Stock)
        .filter(
            offers_models.Stock.offerId == offers_models.Offer.id,
            sa.not_(offers_models.Stock.isSoftDeleted),
        )
        .correlate(offers_models.Offer)
        .scalar_subquery()
    )
    offers = (
        db.session.query(
            offers_models.Offer,
            max_price_subquery.label("max_price"),
        )
        .filter(offers_models.Offer.id.in_(offer_ids))
        .options(
            sa_orm.joinedload(offers_models.Offer.venue.of_type(aliased_venue)).load_only(
                aliased_venue.bookingEmail,
                aliased_venue.name,
                aliased_venue.publicName,
                aliased_venue.managingOffererId,
            ),
            sa_orm.joinedload(offers_models.Offer.offererAddress).options(
                sa_orm.joinedload(offerers_models.OffererAddress.address),
            ),
        )
    ).all()

    for offer, max_price in offers:
        if offer.validation != new_validation:
            was_manually_pending = (
                offer.validation == OfferValidationStatus.PENDING
                and offer.lastValidationType == OfferValidationType.MANUAL
            )

            old_validation = offer.validation
            offer.validation = new_validation
            offer.lastValidationDate = date_utils.get_naive_utc_now()
            offer.lastValidationType = OfferValidationType.MANUAL
            offer.lastValidationAuthorUserId = current_user.id

            is_not_a_future_offer = (
                offer.publicationDatetime is None
                or offer.publicationDatetime <= datetime.datetime.now(datetime.timezone.utc)
            )
            if is_not_a_future_offer:
                offer.publicationDatetime = datetime.datetime.now(datetime.UTC)
            if offer.isThing:
                offer.lastValidationPrice = max_price

            db.session.add(offer)

            if not was_manually_pending:
                # TODO(jbaudet-pass): this might trigger some extra queries
                # -> add missing load option to the offers query
                recipients = _get_offer_recipients(offer)
                offer_data = transactional_mails.get_email_data_from_offer(offer, old_validation, new_validation)
                transactional_mails.send_offer_validation_status_update_email(offer_data, recipients)

    db.session.flush()

    on_commit(
        functools.partial(
            search.async_index_offer_ids,
            offer_ids,
            reason=IndexationReason.OFFER_BATCH_VALIDATION,
        )
    )


def _batch_reject_offers(offer_ids: list[int]) -> None:
    new_validation = offers_models.OfferValidationStatus.REJECTED
    offers = (
        db.session.query(offers_models.Offer)
        .filter(offers_models.Offer.id.in_(offer_ids))
        .options(
            sa_orm.joinedload(offers_models.Offer.venue).load_only(
                offerers_models.Venue.bookingEmail,
                offerers_models.Venue.managingOffererId,
            )
        )
        .all()
    )

    for offer in offers:
        if offer.validation != new_validation:
            old_validation = offer.validation
            offer.validation = new_validation
            offer.lastValidationDate = date_utils.get_naive_utc_now()
            offer.lastValidationType = OfferValidationType.MANUAL
            offer.lastValidationAuthorUserId = current_user.id
            offer.publicationDatetime = None

            # cancel_bookings_from_rejected_offer can raise handled exceptions that drop the
            # modifications of the offer; we save them here first
            db.session.add(offer)
            db.session.flush()

            cancelled_bookings = bookings_api.cancel_bookings_from_rejected_offer(offer)
            for booking in cancelled_bookings:
                transactional_mails.send_booking_cancellation_by_pro_to_beneficiary_email(
                    booking,
                    rejected_by_fraud_action=True,
                )

            db.session.add(offer)
            db.session.flush()

            recipients = _get_offer_recipients(offer)
            offer_data = transactional_mails.get_email_data_from_offer(offer, old_validation, new_validation)
            transactional_mails.send_offer_validation_status_update_email(offer_data, recipients)

    if len(offer_ids) > 0:
        db.session.query(users_models.Favorite).filter(users_models.Favorite.offerId.in_(offer_ids)).delete(
            synchronize_session=False
        )
        db.session.flush()
        on_commit(
            functools.partial(
                search.async_index_offer_ids,
                offer_ids,
                reason=IndexationReason.OFFER_BATCH_VALIDATION,
            )
        )


def _batch_pending_offers(offer_ids: list[int]) -> None:
    db.session.query(offers_models.Offer).filter(offers_models.Offer.id.in_(offer_ids)).update(
        {
            "validation": OfferValidationStatus.PENDING,
            "lastValidationType": OfferValidationType.MANUAL,
            "lastValidationAuthorUserId": current_user.id,
            "lastValidationDate": date_utils.get_naive_utc_now(),
        },
        synchronize_session=False,
    )
    on_commit(
        functools.partial(
            search.async_index_offer_ids,
            offer_ids,
            reason=IndexationReason.OFFER_BATCH_VALIDATION,
        )
    )


def _get_offer_details_actions(offer: offers_models.Offer, threshold: int) -> OfferDetailsActions:
    offer_details_actions = OfferDetailsActions(threshold)
    if offer.isActive and utils.has_current_user_permission(perm_models.Permissions.ADVANCED_PRO_SUPPORT):
        offer_details_actions.add_action(OfferDetailsActionType.DEACTIVATE)
    if not offer.isActive and utils.has_current_user_permission(perm_models.Permissions.ADVANCED_PRO_SUPPORT):
        offer_details_actions.add_action(OfferDetailsActionType.ACTIVATE)
    if utils.has_current_user_permission(perm_models.Permissions.PRO_FRAUD_ACTIONS):
        offer_details_actions.add_action(OfferDetailsActionType.VALIDATE)
        offer_details_actions.add_action(OfferDetailsActionType.PENDING)
        offer_details_actions.add_action(OfferDetailsActionType.REJECT)
    if utils.has_current_user_permission(perm_models.Permissions.MANAGE_OFFERS):
        offer_details_actions.add_action(OfferDetailsActionType.TAG_WEIGHT)
    if utils.has_current_user_permission(perm_models.Permissions.ADVANCED_PRO_SUPPORT):
        offer_details_actions.add_action(OfferDetailsActionType.RESYNC)

    #################################################################################################
    # Caution !!! EDIT_VENUE action is added in get_offer_details to avoid duplicated stock queries #
    #################################################################################################

    return offer_details_actions


@list_offers_blueprint.route("/<int:offer_id>", methods=["GET"])
@utils.permission_required(perm_models.Permissions.READ_OFFERS)
def get_offer_details(offer_id: int) -> utils.BackofficeResponse:
    VenueOffererAddress = sa_orm.aliased(offerers_models.OffererAddress)
    VenueAddress = sa_orm.aliased(geography_models.Address)

    offer_query = (
        db.session.query(offers_models.Offer)
        .filter(offers_models.Offer.id == offer_id)
        .options(
            sa_orm.joinedload(offers_models.Offer.venue).options(
                sa_orm.load_only(
                    offerers_models.Venue.id,
                    offerers_models.Venue.isSoftDeleted,
                    offerers_models.Venue.name,
                    offerers_models.Venue.publicName,
                    offerers_models.Venue.managingOffererId,
                    offerers_models.Venue.siret,
                ),
                sa_orm.joinedload(offerers_models.Venue.managingOfferer).options(
                    sa_orm.load_only(
                        offerers_models.Offerer.id,
                        offerers_models.Offerer.name,
                        offerers_models.Offerer.isActive,
                        offerers_models.Offerer.validationStatus,
                        offerers_models.Offerer.siren,
                    ),
                    sa_orm.joinedload(offerers_models.Offerer.confidenceRule).load_only(
                        offerers_models.OffererConfidenceRule.confidenceLevel
                    ),
                    sa_orm.with_expression(
                        offerers_models.Offerer.isTopActeur,
                        offerers_models.Offerer.is_top_acteur.expression,
                    ),
                ),
                sa_orm.joinedload(offerers_models.Venue.confidenceRule).load_only(
                    offerers_models.OffererConfidenceRule.confidenceLevel
                ),
                sa_orm.joinedload(offerers_models.Venue.offererAddress.of_type(VenueOffererAddress))
                .load_only()
                .joinedload(VenueOffererAddress.address.of_type(VenueAddress))
                .load_only(VenueAddress.departmentCode),
            ),
            sa_orm.joinedload(offers_models.Offer.stocks)
            .joinedload(offers_models.Stock.priceCategory)
            .load_only(offers_models.PriceCategory.price)
            .joinedload(offers_models.PriceCategory.priceCategoryLabel)
            .load_only(offers_models.PriceCategoryLabel.label),
            sa_orm.joinedload(offers_models.Offer.lastValidationAuthor).load_only(
                users_models.User.firstName, users_models.User.lastName
            ),
            sa_orm.joinedload(offers_models.Offer.criteria),
            sa_orm.joinedload(offers_models.Offer.flaggingValidationRules),
            sa_orm.joinedload(offers_models.Offer.mediations),
            sa_orm.joinedload(offers_models.Offer.product).joinedload(offers_models.Product.productMediations),
            sa_orm.joinedload(offers_models.Offer.lastProvider).load_only(providers_models.Provider.name),
            sa_orm.joinedload(offers_models.Offer.offererAddress)
            .load_only(offerers_models.OffererAddress.label)
            .joinedload(offerers_models.OffererAddress.address),
            sa_orm.joinedload(offers_models.Offer.compliance),
            sa_orm.joinedload(offers_models.Offer.metaData),
        )
    )
    offer = offer_query.one_or_none()

    if not offer:
        raise NotFound()

    editable_stock_ids = set()
    if offer.isEvent and not finance_api.are_cashflows_being_generated():
        # store the ids in a set as we will use multiple in on it
        editable_stock_ids = _get_editable_stock(offer_id)

    is_advanced_pro_support = utils.has_current_user_permission(perm_models.Permissions.ADVANCED_PRO_SUPPORT)
    # if the actions count is above this threshold then display the action buttons in a dropdown menu
    allowed_actions = _get_offer_details_actions(offer, threshold=4)

    edit_offer_venue_form = None
    if is_advanced_pro_support:
        try:
            venue_choices = offers_api.check_can_move_event_offer(offer)
            edit_offer_venue_form = forms.EditOfferVenueForm()
            edit_offer_venue_form.set_venue_choices(venue_choices)
            # add the action here to avoid additional stock queries
            allowed_actions.add_action(OfferDetailsActionType.EDIT_VENUE)
        except offers_exceptions.MoveOfferBaseException:
            pass

    connect_as = get_connect_as(
        object_id=offer.id,
        object_type="offer",
        pc_pro_path=urls.build_pc_pro_offer_path(offer),
    )

    return render_template(
        "offer/details.html",
        offer=offer,
        active_tab=request.args.get("active_tab", "stock"),
        editable_stock_ids=editable_stock_ids,
        reindex_offer_form=empty_forms.EmptyForm() if is_advanced_pro_support else None,
        edit_offer_venue_form=edit_offer_venue_form,
        connect_as=connect_as,
        allowed_actions=allowed_actions,
        action=OfferDetailsActionType,
        music_titelive_subcategories=subcategories.MUSIC_TITELIVE_SUBCATEGORY_SEARCH_IDS,
    )


def _get_editable_stock(offer_id: int) -> set[int]:
    raw_stock_ids = (
        db.session.query(offers_models.Stock.id)
        .join(bookings_models.Booking, offers_models.Stock.bookings)
        .join(offers_models.Offer, offers_models.Stock.offer)
        .filter(
            offers_models.Offer.isEvent,
            offers_models.Stock.offerId == offer_id,
            bookings_models.Booking.status.in_(
                (
                    bookings_models.BookingStatus.CONFIRMED,
                    bookings_models.BookingStatus.USED,
                ),
            ),
            offers_models.Stock.id.not_in(
                db.session.query(offers_models.Stock.offerId)
                .join(bookings_models.Booking, offers_models.Stock.bookings)
                .join(finance_models.Pricing, bookings_models.Booking.pricings)
                .filter(
                    finance_models.Pricing.status.in_(
                        (
                            finance_models.PricingStatus.PROCESSED,
                            finance_models.PricingStatus.INVOICED,
                        )
                    ),
                    offers_models.Stock.offerId == offer_id,
                ),
            ),
        )
    )
    return set(stock_id for (stock_id,) in raw_stock_ids)


def _is_stock_editable(offer_id: int, stock_id: int) -> bool:
    return stock_id in _get_editable_stock(offer_id)


def _manage_price_category(stock: offers_models.Stock, new_price: float) -> bool:
    if stock.priceCategory is None:
        return False

    stock_count = (
        db.session.query(sa.func.count(offers_models.Stock.id))
        .filter(offers_models.Stock.priceCategoryId == stock.priceCategoryId)
        .scalar()
    )

    if stock_count == 1:
        stock.priceCategory.price = decimal.Decimal(str(new_price))
        db.session.add(stock.priceCategory)
        return False

    new_price_category_label = offers_models.PriceCategoryLabel(
        label=f"{stock.priceCategory.priceCategoryLabel.label} - Revalorisation du {datetime.date.today().strftime('%d/%m/%Y')}",
        venue=stock.priceCategory.priceCategoryLabel.venue,
    )
    db.session.add(new_price_category_label)
    new_price_category = offers_models.PriceCategory(
        offerId=stock.offerId,
        price=decimal.Decimal(new_price),
        priceCategoryLabel=new_price_category_label,
    )
    db.session.add(new_price_category)
    stock.priceCategory = new_price_category
    db.session.add(stock)
    return True


@list_offers_blueprint.route("/<int:offer_id>/stock/<int:stock_id>/edit", methods=["POST"])
@utils.permission_required(perm_models.Permissions.MANAGE_OFFERS)
def edit_offer_stock(offer_id: int, stock_id: int) -> utils.BackofficeResponse:
    stock = (
        db.session.query(offers_models.Stock)
        .filter(
            offers_models.Stock.id == stock_id,
        )
        .options(
            sa_orm.joinedload(offers_models.Stock.priceCategory).joinedload(
                offers_models.PriceCategory.priceCategoryLabel
            ),
        )
        .one()
    )

    if stock.offerId != offer_id:
        mark_transaction_as_invalid()
        flash("L'offer_id et le stock_id ne sont pas cohérents.", "warning")
        return redirect(url_for("backoffice_web.offer.get_offer_details", offer_id=offer_id), 303)
    if finance_api.are_cashflows_being_generated():
        mark_transaction_as_invalid()
        flash("Le script de génération des cashflows est en cours, veuillez réessayer plus tard.", "warning")
        return redirect(url_for("backoffice_web.offer.get_offer_details", offer_id=offer_id), 303)
    if not _is_stock_editable(offer_id, stock_id):
        mark_transaction_as_invalid()
        flash("Ce stock n'est pas éditable.", "warning")
        return redirect(url_for("backoffice_web.offer.get_offer_details", offer_id=offer_id), 303)

    form = forms.EditStockForm(old_price=stock.price)
    old_price = stock.price

    if not form.validate():
        mark_transaction_as_invalid()
        flash(utils.build_form_error_msg(form), "warning")
        return redirect(url_for("backoffice_web.offer.get_offer_details", offer_id=offer_id), 303)

    new_price = 0.0
    if form.price.data:
        new_price = float(form.price.data)
        offers_api.update_used_stock_price(stock=stock, new_price=form.price.data)

    if form.percent.data:
        price_percent = decimal.Decimal((100 - float(form.percent.data)) / 100)
        new_price = float(stock.price * price_percent)
        offers_api.update_used_stock_price(stock=stock, price_percent=price_percent)

    db.session.flush()
    if _manage_price_category(stock, new_price):
        flash(f"Le stock {stock_id} a été mis à jour et un nouveau tarif a été créé", "success")
    else:
        flash(f"Le stock {stock_id} a été mis à jour.", "success")
    logger.info(
        "A past stock price was updated by an administrator",
        extra={
            "user_id": current_user.id,
            "stock_id": stock_id,
            "old_price": float(old_price),
            "new_price": float(new_price),
        },
    )

    return redirect(url_for("backoffice_web.offer.get_offer_details", offer_id=offer_id), 303)


@list_offers_blueprint.route("/<int:offer_id>/stock/<int:stock_id>/confirm", methods=["POST"])
@utils.permission_required(perm_models.Permissions.MANAGE_OFFERS)
def confirm_offer_stock(offer_id: int, stock_id: int) -> utils.BackofficeResponse:
    stock = db.session.query(offers_models.Stock).filter_by(id=stock_id).one()

    if stock.offerId != offer_id:
        alert = "L'offer_id et le stock_id ne sont pas cohérents."
        return _generate_offer_stock_edit_form(offer_id, stock_id, alert=alert)
    if finance_api.are_cashflows_being_generated():
        alert = "Le script de génération des cashflows est en cours, veuillez réessayer plus tard."
        return _generate_offer_stock_edit_form(offer_id, stock_id, alert=alert)

    if not _is_stock_editable(offer_id, stock_id):
        alert = "Ce stock n'est pas éditable."
        return _generate_offer_stock_edit_form(offer_id, stock_id, alert=alert)

    form = forms.EditStockForm(old_price=stock.price)

    if not form.validate():
        mark_transaction_as_invalid()
        return _generate_offer_stock_edit_form(offer_id, stock_id, form)

    alert = ""
    Effect = namedtuple("Effect", ["quantity", "old_price", "new_price", "warning"])
    price_effect = []
    for quantity, amount in _get_count_booking_prices_for_stock(stock):
        if form.price.data:
            new_price = min(amount, form.price.data)
            if new_price != form.price.data:
                alert = "Cette modification amènerait à augmenter le prix de certaines réservations. Celles-ci ne seront pas changées"
            price_effect.append(Effect(quantity, amount, new_price, new_price != form.price.data))
        elif form.percent.data:
            price_effect.append(
                Effect(
                    quantity,
                    amount,
                    round((amount * (1 - form.percent.data / 100)), 2),
                    False,
                )
            )

    return render_template(
        "offer/confirm_stock_price_change.html",
        form=form,
        dst=url_for("backoffice_web.offer.edit_offer_stock", offer_id=offer_id, stock_id=stock_id),
        div_id=f"edit-offer-stock-modal-{stock_id}",
        title=f"Baisser le prix du stock {stock_id}",
        button_text="Continuer",
        information="Nombre de réservations actives par prix :",
        price_effect=price_effect,
        stock=stock,
        alert=alert,
    )


@list_offers_blueprint.route("/<int:offer_id>/stock/<int:stock_id>/edit", methods=["GET"])
@utils.permission_required(perm_models.Permissions.MANAGE_OFFERS)
def get_offer_stock_edit_form(
    offer_id: int,
    stock_id: int,
    form: forms.EditStockForm | None = None,
) -> utils.BackofficeResponse:
    if finance_api.are_cashflows_being_generated():
        return render_template(
            "components/dynamic/modal_form.html",
            div_id=f"edit-offer-stock-modal-{stock_id}",
            title=f"Baisser le prix du stock {stock_id}",
            alert="Le script de génération des cashflows est en cours, veuillez réessayer plus tard.",
        )

    if not _is_stock_editable(offer_id, stock_id):
        return render_template(
            "components/dynamic/modal_form.html",
            div_id=f"edit-offer-stock-modal-{stock_id}",
            title=f"Baisser le prix du stock {stock_id}",
            alert="Ce stock n'est pas éditable.",
        )
    return _generate_offer_stock_edit_form(offer_id, stock_id)


def _generate_offer_stock_edit_form(
    offer_id: int,
    stock_id: int,
    form: forms.EditStockForm | None = None,
    alert: str | None = None,
) -> utils.BackofficeResponse:
    stock = db.session.query(offers_models.Stock).filter_by(id=stock_id).one()

    form = form or forms.EditStockForm(old_price=stock.price)
    return render_template(
        "components/dynamic/modal_form.html",
        form=form,
        dst=url_for("backoffice_web.offer.confirm_offer_stock", offer_id=offer_id, stock_id=stock_id),
        div_id=f"edit-offer-stock-modal-{stock_id}",
        title=f"Baisser le prix du stock {stock_id}",
        button_text="Continuer",
        information="Nombre de réservations actives par prix :",
        additional_data=(
            (f"{q} réservation{pluralize(q)}", format_amount(a)) for q, a in _get_count_booking_prices_for_stock(stock)
        ),
        alert=alert,
        close_on_validation=False,
    )


def _get_count_booking_prices_for_stock(stock: offers_models.Stock) -> list[tuple[int, decimal.Decimal]]:
    bookings = (
        db.session.query(bookings_models.Booking)
        .with_entities(
            bookings_models.Booking.amount,
            sa.func.count(bookings_models.Booking.id).label("quantity"),
        )
        .filter(
            bookings_models.Booking.stockId == stock.id,
            bookings_models.Booking.status != bookings_models.BookingStatus.CANCELLED,
        )
        .group_by(
            bookings_models.Booking.amount,
        )
        .order_by(
            bookings_models.Booking.amount,
        )
    )
    return [(booking.quantity, booking.amount) for booking in bookings]


@list_offers_blueprint.route("/<int:offer_id>/reindex", methods=["POST"])
@utils.permission_required(perm_models.Permissions.ADVANCED_PRO_SUPPORT)
def reindex(offer_id: int) -> utils.BackofficeResponse:
    search.async_index_offer_ids(
        {offer_id},
        reason=IndexationReason.OFFER_MANUAL_REINDEXATION,
    )

    flash("La resynchronisation de l'offre a été demandée.", "success")
    return redirect(url_for("backoffice_web.offer.get_offer_details", offer_id=offer_id), 303)


@list_offers_blueprint.route("/<int:offer_id>/edit-venue", methods=["POST"])
@utils.permission_required(perm_models.Permissions.ADVANCED_PRO_SUPPORT)
def edit_offer_venue(offer_id: int) -> utils.BackofficeResponse:
    offer_url = url_for("backoffice_web.offer.get_offer_details", offer_id=offer_id)

    offer = (
        db.session.query(offers_models.Offer)
        .filter_by(id=offer_id)
        .options(sa_orm.joinedload(offers_models.Offer.venue))
        .one_or_none()
    )
    if not offer:
        raise NotFound()

    try:
        form = forms.EditOfferVenueForm()
        if not form.validate():
            mark_transaction_as_invalid()
            flash(utils.build_form_error_msg(form), "warning")
            return redirect(offer_url, 303)

        destination_venue = (
            db.session.query(offerers_models.Venue)
            .filter_by(id=int(form.venue.data))
            .outerjoin(
                offerers_models.VenuePricingPointLink,
                sa.and_(
                    offerers_models.VenuePricingPointLink.venueId == offerers_models.Venue.id,
                    offerers_models.VenuePricingPointLink.timespan.contains(date_utils.get_naive_utc_now()),
                ),
            )
            .options(
                sa_orm.contains_eager(offerers_models.Venue.pricing_point_links).load_only(
                    offerers_models.VenuePricingPointLink.pricingPointId, offerers_models.VenuePricingPointLink.timespan
                ),
            )
            .options(sa_orm.joinedload(offerers_models.Venue.offererAddress))
        ).one()

        offers_api.move_event_offer(
            offer,
            destination_venue,
            move_offer_address=form.move_offer_address.data,
            notify_beneficiary=form.notify_beneficiary.data,
        )

    except offers_exceptions.MoveOfferBaseException as exc:
        mark_transaction_as_invalid()
        flash(
            Markup("Le partenaire culturel de cette offre ne peut pas être modifié : {reason}").format(reason=str(exc)),
            "warning",
        )
        return redirect(offer_url, 303)

    flash(
        Markup("L'offre a été déplacée vers le partenaire culturel <b>{venue_name}</b>").format(
            venue_name=destination_venue.common_name
        ),
        "success",
    )
    return redirect(offer_url, 303)


@list_offers_blueprint.route("/<int:offer_id>/bookings.csv", methods=["GET"])
def download_bookings_csv(offer_id: int) -> utils.BackofficeResponse:
    export_data = booking_repository.get_export(
        user=current_user,
        offer_id=offer_id,
        export_type=bookings_models.BookingExportType.CSV,
    )
    buffer = BytesIO(typing.cast(str, export_data).encode("utf-8-sig"))
    return send_file(
        buffer,
        as_attachment=True,
        download_name=f"reservations_offre_{offer_id}.csv",
        mimetype="text/csv",
    )


@list_offers_blueprint.route("/<int:offer_id>/bookings.xlsx", methods=["GET"])
def download_bookings_xlsx(offer_id: int) -> utils.BackofficeResponse:
    export_data = booking_repository.get_export(
        user=current_user,
        offer_id=offer_id,
        export_type=bookings_models.BookingExportType.EXCEL,
    )
    buffer = BytesIO(typing.cast(bytes, export_data))
    return send_file(
        buffer,
        as_attachment=True,
        download_name=f"reservations_offre_{offer_id}.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )


@list_offers_blueprint.route("/<int:offer_id>/activate", methods=["GET"])
@utils.permission_required(perm_models.Permissions.ADVANCED_PRO_SUPPORT)
def get_activate_offer_form(offer_id: int) -> utils.BackofficeResponse:
    offer = db.session.query(offers_models.Offer).filter_by(id=offer_id).one_or_none()

    if not offer:
        raise NotFound()

    form = empty_forms.DynamicForm(formdata=utils.get_query_params())

    return render_template(
        "components/dynamic/modal_form.html",
        target_id=f"#offer-row-{offer_id}",
        form=form,
        dst=url_for("backoffice_web.offer.activate_offer", offer_id=offer.id),
        div_id=f"activate-offer-modal-{offer.id}",
        title=f"Publication de l'offre {offer.name}",
        button_text="Publier l'offre",
        ajax_submit=not form.redirect.data,
    )


@list_offers_blueprint.route("/<int:offer_id>/deactivate", methods=["GET"])
@utils.permission_required(perm_models.Permissions.ADVANCED_PRO_SUPPORT)
def get_deactivate_offer_form(offer_id: int) -> utils.BackofficeResponse:
    offer = db.session.query(offers_models.Offer).filter_by(id=offer_id).one_or_none()

    if not offer:
        raise NotFound()

    form = empty_forms.DynamicForm(formdata=utils.get_query_params())

    return render_template(
        "components/dynamic/modal_form.html",
        target_id=f"#offer-row-{offer_id}",
        form=form,
        dst=url_for("backoffice_web.offer.deactivate_offer", offer_id=offer.id),
        div_id=f"deactivate-offer-modal-{offer.id}",
        title=f"Mise en pause de l'offre {offer.name}",
        information="L’acteur pourra réactiver l’offre",
        button_text="Mettre l'offre en pause",
        ajax_submit=not form.redirect.data,
    )


@list_offers_blueprint.route("/batch/activate", methods=["POST"])
@utils.permission_required(perm_models.Permissions.ADVANCED_PRO_SUPPORT)
def get_batch_activate_offers_form() -> utils.BackofficeResponse:
    form = empty_forms.BatchForm()
    return render_template(
        "components/dynamic/modal_form.html",
        target_id="#offers-table",
        form=form,
        dst=url_for("backoffice_web.offer.batch_activate_offers"),
        div_id="batch-activate-offer-modal",
        title="Voulez-vous publier les offres sélectionnées ?",
        button_text="Publier",
    )


@list_offers_blueprint.route("/batch/deactivate", methods=["POST"])
@utils.permission_required(perm_models.Permissions.ADVANCED_PRO_SUPPORT)
def get_batch_deactivate_offers_form() -> utils.BackofficeResponse:
    form = empty_forms.BatchForm()
    return render_template(
        "components/dynamic/modal_form.html",
        target_id="#offers-table",
        form=form,
        dst=url_for("backoffice_web.offer.batch_deactivate_offers"),
        div_id="batch-deactivate-offer-modal",
        title="Voulez-vous mettre en pause les offres sélectionnées ?",
        information="L’acteur pourra réactiver les offres",
        button_text="Mettre en pause",
    )


def _batch_update_activation_offers(offer_ids: list[int], *, is_active: bool) -> None:
    query = db.session.query(offers_models.Offer).filter(offers_models.Offer.id.in_(offer_ids))
    offers_api.batch_update_offers(query, activate=is_active)


@list_offers_blueprint.route("/<int:offer_id>/activate", methods=["POST"])
@utils.permission_required(perm_models.Permissions.ADVANCED_PRO_SUPPORT)
def activate_offer(offer_id: int) -> utils.BackofficeResponse:
    _batch_update_activation_offers([offer_id], is_active=True)
    flash("L'offre a été publiée", "success")
    if utils.is_request_from_htmx():
        return _render_offer_rows([offer_id])
    return redirect(request.referrer or url_for("backoffice_web.offer.list_offers"), 303)


@list_offers_blueprint.route("/batch-activate", methods=["POST"])
@utils.permission_required(perm_models.Permissions.ADVANCED_PRO_SUPPORT)
def batch_activate_offers() -> utils.BackofficeResponse:
    form = empty_forms.BatchForm()
    if not form.validate():
        mark_transaction_as_invalid()
        flash(utils.build_form_error_msg(form), "warning")
        return redirect(request.referrer, 400)

    _batch_update_activation_offers(form.object_ids_list, is_active=True)
    flash("Les offres ont été publiées", "success")
    return _render_offer_rows(form.object_ids_list)


@list_offers_blueprint.route("/<int:offer_id>/deactivate", methods=["POST"])
@utils.permission_required(perm_models.Permissions.ADVANCED_PRO_SUPPORT)
def deactivate_offer(offer_id: int) -> utils.BackofficeResponse:
    _batch_update_activation_offers([offer_id], is_active=False)
    flash("L'offre a été mise en pause, l’acteur pourra la réactiver", "success")
    if utils.is_request_from_htmx():
        return _render_offer_rows([offer_id])
    return redirect(request.referrer or url_for("backoffice_web.offer.list_offers"), 303)


@list_offers_blueprint.route("/batch-deactivate", methods=["POST"])
@utils.permission_required(perm_models.Permissions.ADVANCED_PRO_SUPPORT)
def batch_deactivate_offers() -> utils.BackofficeResponse:
    form = empty_forms.BatchForm()
    if not form.validate():
        mark_transaction_as_invalid()
        flash(utils.build_form_error_msg(form), "warning")
        return redirect(request.referrer, 400)

    _batch_update_activation_offers(form.object_ids_list, is_active=False)
    flash("Les offres ont été mises en pause, l’acteur pourra les réactiver", "success")
    return _render_offer_rows(form.object_ids_list)
