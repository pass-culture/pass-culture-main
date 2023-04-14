from flask import request
import sqlalchemy as sa

from pcapi.core.criteria import models as criteria_models
from pcapi.core.finance import models as finance_models
from pcapi.core.offerers import models as offerers_models
from pcapi.routes.serialization import BaseModel
from pcapi.serialization.decorator import spectree_serialize
from pcapi.utils.clean_accents import clean_accents

from . import blueprint
from .forms import fields


NUM_RESULTS = 20


class AutocompleteItem(BaseModel):
    id: int
    text: str


class AutocompleteResponse(BaseModel):
    items: list[AutocompleteItem]


def _get_offerer_choice_label(offerer: offerers_models.Offerer) -> str:
    return f"{offerer.name} ({offerer.siren})"


def _get_offerers_base_query() -> sa.orm.Query:
    return offerers_models.Offerer.query.options(
        sa.orm.load_only(
            offerers_models.Offerer.id,
            offerers_models.Offerer.name,
            offerers_models.Offerer.siren,
        )
    )


def prefill_offerers_choices(autocomplete_field: fields.PCTomSelectField) -> None:
    if autocomplete_field.data:
        offerers = (
            _get_offerers_base_query()
            .filter(offerers_models.Offerer.id.in_(autocomplete_field.data))
            .order_by(offerers_models.Offerer.name)
        )
        autocomplete_field.choices = [(offerer.id, _get_offerer_choice_label(offerer)) for offerer in offerers]


@blueprint.backoffice_v3_web.route("/autocomplete/offerers", methods=["GET"])
@spectree_serialize(response_model=AutocompleteResponse, api=blueprint.backoffice_v3_web_schema)
def autocomplete_offerers() -> AutocompleteResponse:
    query_string = request.args.get("q", "").strip()

    if len(query_string) < 2:
        return AutocompleteResponse(items=[])

    filters = sa.func.unaccent(offerers_models.Offerer.name).ilike(f"%{clean_accents(query_string)}%")

    if query_string.isnumeric() and len(query_string) <= 9:
        filters = sa.or_(filters, offerers_models.Offerer.siren.like(f"{query_string}%"))

    offerers = _get_offerers_base_query().filter(filters).limit(NUM_RESULTS)

    return AutocompleteResponse(
        items=[AutocompleteItem(id=offerer.id, text=_get_offerer_choice_label(offerer)) for offerer in offerers]
    )


def _get_venue_choice_label(venue: offerers_models.Venue) -> str:
    return f"{venue.name} ({venue.siret or 'Pas de SIRET'})"


def _get_venues_base_query() -> sa.orm.Query:
    return offerers_models.Venue.query.options(
        sa.orm.load_only(
            offerers_models.Venue.id,
            offerers_models.Venue.name,
            offerers_models.Venue.siret,
        )
    )


def prefill_venues_choices(autocomplete_field: fields.PCTomSelectField) -> None:
    if autocomplete_field.data:
        venues = (
            _get_venues_base_query()
            .filter(offerers_models.Venue.id.in_(autocomplete_field.data))
            .order_by(offerers_models.Venue.name)
        )
        autocomplete_field.choices = [(venue.id, _get_venue_choice_label(venue)) for venue in venues]


@blueprint.backoffice_v3_web.route("/autocomplete/venues", methods=["GET"])
@spectree_serialize(response_model=AutocompleteResponse, api=blueprint.backoffice_v3_web_schema)
def autocomplete_venues() -> AutocompleteResponse:
    query_string = request.args.get("q", "").strip()

    if not query_string or len(query_string) < 2:
        return AutocompleteResponse(items=[])

    filters = sa.func.unaccent(offerers_models.Venue.name).ilike(f"%{clean_accents(query_string)}%")

    if query_string.isnumeric() and len(query_string) <= 14:
        filters = sa.or_(filters, offerers_models.Venue.siret.like(f"{query_string}%"))

    venues = _get_venues_base_query().filter(filters).limit(NUM_RESULTS)

    return AutocompleteResponse(
        items=[AutocompleteItem(id=venue.id, text=_get_venue_choice_label(venue)) for venue in venues]
    )


def _get_criterion_choice_label(criterion: criteria_models.Criterion) -> str:
    label = criterion.name
    if criterion.startDateTime or criterion.endDateTime:
        label += (
            f" ({criterion.startDateTime.strftime('%d/%m/%Y') if criterion.startDateTime else '…'}-"
            f"{criterion.endDateTime.strftime('%d/%m/%Y') if criterion.endDateTime else '…'})"
        )
    return label


def _get_criteria_base_query() -> sa.orm.Query:
    return criteria_models.Criterion.query.options(
        sa.orm.load_only(
            criteria_models.Criterion.id,
            criteria_models.Criterion.name,
            criteria_models.Criterion.startDateTime,
            criteria_models.Criterion.endDateTime,
        )
    )


def prefill_criteria_choices(autocomplete_field: fields.PCTomSelectField) -> None:
    if autocomplete_field.data:
        criteria = (
            _get_criteria_base_query()
            .filter(criteria_models.Criterion.id.in_(autocomplete_field.data))
            .order_by(criteria_models.Criterion.name)
            .all()
        )
        autocomplete_field.choices = [(criterion.id, _get_criterion_choice_label(criterion)) for criterion in criteria]


@blueprint.backoffice_v3_web.route("/autocomplete/criteria", methods=["GET"])
@spectree_serialize(response_model=AutocompleteResponse, api=blueprint.backoffice_v3_web_schema)
def autocomplete_criteria() -> AutocompleteResponse:
    query_string = request.args.get("q", "").strip()

    if not query_string or len(query_string) < 2:
        return AutocompleteResponse(items=[])

    criteria = (
        _get_criteria_base_query()
        .filter(sa.func.unaccent(criteria_models.Criterion.name).ilike(f"%{clean_accents(query_string)}%"))
        .limit(NUM_RESULTS)
        .all()
    )

    return AutocompleteResponse(
        items=[AutocompleteItem(id=criterion.id, text=_get_criterion_choice_label(criterion)) for criterion in criteria]
    )


def _get_cashflow_batches_base_query() -> sa.orm.Query:
    return finance_models.CashflowBatch.query.options(
        sa.orm.load_only(
            finance_models.CashflowBatch.id,
            finance_models.CashflowBatch.label,
        )
    )


def prefill_cashflow_batch_choices(autocomplete_field: fields.PCTomSelectField) -> None:
    if autocomplete_field.data:
        cashflow_batches = (
            _get_cashflow_batches_base_query()
            .filter(finance_models.CashflowBatch.id.in_(autocomplete_field.data))
            .order_by(finance_models.CashflowBatch.label)
        )
        autocomplete_field.choices = [(cashflow_batch.id, cashflow_batch.label) for cashflow_batch in cashflow_batches]


@blueprint.backoffice_v3_web.route("/autocomplete/cashflow-batches", methods=["GET"])
@spectree_serialize(response_model=AutocompleteResponse, api=blueprint.backoffice_v3_web_schema)
def autocomplete_cashflow_batches() -> AutocompleteResponse:
    query_string = request.args.get("q", "").strip()

    if len(query_string) < 2:
        return AutocompleteResponse(items=[])

    filters = finance_models.CashflowBatch.label.ilike(f"%{query_string}%")

    cashflow_batches = _get_cashflow_batches_base_query().filter(filters).limit(NUM_RESULTS)

    return AutocompleteResponse(
        items=[AutocompleteItem(id=cashflow_batch.id, text=cashflow_batch.label) for cashflow_batch in cashflow_batches]
    )
