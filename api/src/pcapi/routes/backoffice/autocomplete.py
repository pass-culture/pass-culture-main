import re

from flask import request
from flask_login import login_required
import sqlalchemy as sa

from pcapi.connectors import api_adresse
from pcapi.core.criteria import models as criteria_models
from pcapi.core.educational import models as educational_models
from pcapi.core.finance import models as finance_models
from pcapi.core.geography import models as geography_models
from pcapi.core.offerers import models as offerers_models
from pcapi.core.providers import models as providers_models
from pcapi.core.users import models as users_models
from pcapi.repository import atomic
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
    return f"{offerer.id} - {offerer.name} ({offerer.siren})"


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


@blueprint.backoffice_web.route("/autocomplete/offerers", methods=["GET"])
@atomic()
@login_required
@spectree_serialize(response_model=AutocompleteResponse, api=blueprint.backoffice_web_schema)
def autocomplete_offerers() -> AutocompleteResponse:
    query_string = request.args.get("q", "").strip()

    is_numeric_query = query_string.isnumeric()
    if not is_numeric_query and len(query_string) < 2:
        return AutocompleteResponse(items=[])

    if is_numeric_query and len(query_string) == 1:
        filters = offerers_models.Offerer.id == int(query_string)
    else:
        filters = sa.func.immutable_unaccent(offerers_models.Offerer.name).ilike(f"%{clean_accents(query_string)}%")

        if is_numeric_query and len(query_string) <= 9:
            filters = sa.or_(
                filters,
                offerers_models.Offerer.id == int(query_string),
                offerers_models.Offerer.siren.like(f"{query_string}%"),
            )

    offerers = _get_offerers_base_query().filter(filters).limit(NUM_RESULTS)

    return AutocompleteResponse(
        items=[AutocompleteItem(id=offerer.id, text=_get_offerer_choice_label(offerer)) for offerer in offerers]
    )


def _get_institution_choice_label(institution: educational_models.EducationalInstitution) -> str:
    return (
        f"{institution.institutionType} {institution.name.strip()} - {institution.city} ({institution.institutionId})"
    )


def _get_institutions_base_query() -> sa.orm.Query:
    return educational_models.EducationalInstitution.query.options(
        sa.orm.load_only(
            educational_models.EducationalInstitution.id,
            educational_models.EducationalInstitution.name,
            educational_models.EducationalInstitution.institutionId,
            educational_models.EducationalInstitution.institutionType,
            educational_models.EducationalInstitution.city,
        )
    )


def prefill_institutions_choices(autocomplete_field: fields.PCTomSelectField) -> None:
    if autocomplete_field.data:
        institutions = (
            _get_institutions_base_query()
            .filter(educational_models.EducationalInstitution.id.in_(autocomplete_field.data))
            .order_by(
                educational_models.EducationalInstitution.institutionType,
                educational_models.EducationalInstitution.name,
            )
        )
        autocomplete_field.choices = [
            (institution.id, _get_institution_choice_label(institution)) for institution in institutions
        ]


@blueprint.backoffice_web.route("/autocomplete/institutions", methods=["GET"])
@atomic()
@login_required
@spectree_serialize(response_model=AutocompleteResponse, api=blueprint.backoffice_web_schema)
def autocomplete_institutions() -> AutocompleteResponse:
    query_string = request.args.get("q", "").strip()

    is_numeric_query = query_string.isnumeric()
    if not is_numeric_query and len(query_string) < 2:
        return AutocompleteResponse(items=[])

    if is_numeric_query:
        filters = educational_models.EducationalInstitution.id == int(query_string)
    elif re.match(r"^\d{7}\w{1}$", query_string):
        filters = educational_models.EducationalInstitution.institutionId == query_string
    else:
        searched_name = (
            educational_models.EducationalInstitution.institutionType
            + " "
            + educational_models.EducationalInstitution.name
            + " "
            + educational_models.EducationalInstitution.city
        )
        # Don't use sa.func.unaccent on query, as it will skip the use of the index
        # Besides, all three columns are accentless in db
        filters = searched_name.ilike(f"%{clean_accents(query_string).replace(' ', '%')}%")
    institutions = _get_institutions_base_query().filter(filters).limit(NUM_RESULTS)

    return AutocompleteResponse(
        items=[
            AutocompleteItem(id=institution.id, text=_get_institution_choice_label(institution))
            for institution in institutions
        ]
    )


def _get_venue_choice_label(venue: offerers_models.Venue) -> str:
    return f"{venue.id} - {venue.common_name} ({venue.siret or 'Pas de SIRET'})"


def _get_venues_base_query() -> sa.orm.Query:
    return offerers_models.Venue.query.options(
        sa.orm.load_only(
            offerers_models.Venue.id,
            offerers_models.Venue.name,
            offerers_models.Venue.publicName,
            offerers_models.Venue.siret,
        )
    )


def prefill_providers_choices(autocomplete_field: fields.PCTomSelectField) -> None:
    if autocomplete_field.data:
        providers = (
            providers_models.Provider.query.filter(
                providers_models.Provider.id.in_(autocomplete_field.data),
                providers_models.Provider.isActive,
            )
            .order_by(providers_models.Provider.name)
            .options(sa.orm.load_only(providers_models.Provider.id, providers_models.Provider.name))
        )
        autocomplete_field.choices = [(provider.id, f"{provider.id} - {provider.name}") for provider in providers]


def prefill_venues_choices(autocomplete_field: fields.PCTomSelectField, only_with_siret: bool = False) -> None:
    if autocomplete_field.data:
        venues = (
            _get_venues_base_query()
            .filter(offerers_models.Venue.id.in_(autocomplete_field.data))
            .order_by(offerers_models.Venue.common_name)
        )
        if only_with_siret:
            venues = venues.filter(offerers_models.Venue.siret.is_not(None))
        autocomplete_field.choices = [(venue.id, _get_venue_choice_label(venue)) for venue in venues]


def _autocomplete_venues(only_with_siret: bool = False) -> AutocompleteResponse:
    query_string = request.args.get("q", "").strip()

    is_numeric_query = query_string.isnumeric()
    if not is_numeric_query and len(query_string) < 2:
        return AutocompleteResponse(items=[])

    if is_numeric_query and len(query_string) == 1:
        filters = offerers_models.Venue.id == int(query_string)
    else:
        or_filters = [
            sa.func.immutable_unaccent(offerers_models.Venue.name).ilike(f"%{clean_accents(query_string)}%"),
            sa.func.immutable_unaccent(offerers_models.Venue.publicName).ilike(f"%{clean_accents(query_string)}%"),
        ]

        if is_numeric_query and len(query_string) <= 14:
            or_filters += [
                offerers_models.Venue.id == int(query_string),
                offerers_models.Venue.siret.like(f"{query_string}%"),
            ]

        filters = sa.or_(*or_filters)
    if only_with_siret:
        filters = sa.and_(filters, offerers_models.Venue.siret.is_not(None))

    venues = _get_venues_base_query().filter(filters).limit(NUM_RESULTS)
    return AutocompleteResponse(
        items=[AutocompleteItem(id=venue.id, text=_get_venue_choice_label(venue)) for venue in venues]
    )


@blueprint.backoffice_web.route("/autocomplete/venues", methods=["GET"])
@atomic()
@login_required
@spectree_serialize(response_model=AutocompleteResponse, api=blueprint.backoffice_web_schema)
def autocomplete_venues() -> AutocompleteResponse:
    return _autocomplete_venues()


@blueprint.backoffice_web.route("/autocomplete/pricing-points", methods=["GET"])
@atomic()
@login_required
@spectree_serialize(response_model=AutocompleteResponse, api=blueprint.backoffice_web_schema)
def autocomplete_pricing_points() -> AutocompleteResponse:
    return _autocomplete_venues(only_with_siret=True)


@blueprint.backoffice_web.route("/autocomplete/providers", methods=["GET"])
@atomic()
@login_required
@spectree_serialize(response_model=AutocompleteResponse, api=blueprint.backoffice_web_schema)
def autocomplete_providers() -> AutocompleteResponse:
    query_string = request.args.get("q", "").strip()

    query = providers_models.Provider.query.filter(providers_models.Provider.isActive).options(
        sa.orm.load_only(providers_models.Provider.id, providers_models.Provider.name)
    )
    if query_string.isnumeric():
        query = query.filter(providers_models.Provider.id == int(query_string))
    elif query_string:
        query = query.filter(sa.func.unaccent(providers_models.Provider.name).ilike(f"%{clean_accents(query_string)}%"))
    else:
        return AutocompleteResponse(items=[])

    providers = query.limit(NUM_RESULTS)
    return AutocompleteResponse(
        items=[AutocompleteItem(id=provider.id, text=f"{provider.id} - {provider.name}") for provider in providers]
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


@blueprint.backoffice_web.route("/autocomplete/criteria", methods=["GET"])
@atomic()
@login_required
@spectree_serialize(response_model=AutocompleteResponse, api=blueprint.backoffice_web_schema)
def autocomplete_criteria() -> AutocompleteResponse:
    query_string = request.args.get("q", "").strip()

    if not query_string.isnumeric() and len(query_string) < 2:
        return AutocompleteResponse(items=[])

    if query_string.isnumeric():
        criteria = _get_criteria_base_query().filter(criteria_models.Criterion.id == int(query_string)).all()
    else:
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


@blueprint.backoffice_web.route("/autocomplete/cashflow-batches", methods=["GET"])
@atomic()
@login_required
@spectree_serialize(response_model=AutocompleteResponse, api=blueprint.backoffice_web_schema)
def autocomplete_cashflow_batches() -> AutocompleteResponse:
    query_string = request.args.get("q", "").strip()

    if len(query_string) < 2:
        return AutocompleteResponse(items=[])

    filters = finance_models.CashflowBatch.label.ilike(f"%{query_string}%")

    cashflow_batches = _get_cashflow_batches_base_query().filter(filters).limit(NUM_RESULTS)

    return AutocompleteResponse(
        items=[AutocompleteItem(id=cashflow_batch.id, text=cashflow_batch.label) for cashflow_batch in cashflow_batches]
    )


def _get_bo_users_base_query() -> sa.orm.Query:
    return users_models.User.query.join(users_models.User.backoffice_profile).options(
        sa.orm.load_only(users_models.User.id, users_models.User.firstName, users_models.User.lastName)
    )


def prefill_bo_users_choices(autocomplete_field: fields.PCTomSelectField) -> None:
    if autocomplete_field.data:
        users = (
            _get_bo_users_base_query()
            .filter(users_models.User.id.in_(autocomplete_field.data))
            .order_by(users_models.User.full_name)
        )
        autocomplete_field.choices = [(user.id, user.full_name) for user in users]


@blueprint.backoffice_web.route("/autocomplete/bo-users", methods=["GET"])
@atomic()
@login_required
@spectree_serialize(response_model=AutocompleteResponse, api=blueprint.backoffice_web_schema)
def autocomplete_bo_users() -> AutocompleteResponse:
    query_string = request.args.get("q", "").strip()

    is_numeric_query = query_string.isnumeric()
    if not is_numeric_query and len(query_string) < 2:
        return AutocompleteResponse(items=[])

    if is_numeric_query:
        query_filter = users_models.User.id == int(query_string)
    else:
        query_filter = sa.func.immutable_unaccent(users_models.User.firstName + " " + users_models.User.lastName).ilike(
            f"%{clean_accents(query_string)}%"
        )

    users = _get_bo_users_base_query().filter(query_filter).limit(NUM_RESULTS)

    return AutocompleteResponse(items=[AutocompleteItem(id=user.id, text=user.full_name) for user in users])


def _get_address_choice_label(address: geography_models.Address) -> str:
    return f"{address.street} {address.postalCode} {address.city}"


def _get_addresses_base_query() -> sa.orm.Query:
    return geography_models.Address.query.options(
        sa.orm.load_only(
            geography_models.Address.id,
            geography_models.Address.street,
            geography_models.Address.postalCode,
            geography_models.Address.city,
        )
    )


def prefill_addresses_choices(autocomplete_field: fields.PCTomSelectField) -> None:
    if autocomplete_field.data:
        addresses = (
            _get_addresses_base_query()
            .filter(geography_models.Address.id.in_(autocomplete_field.data))
            .order_by(geography_models.Address.id)
        )
        autocomplete_field.choices = [(address.id, _get_address_choice_label(address)) for address in addresses]


@blueprint.backoffice_web.route("/autocomplete/addresses", methods=["GET"])
@login_required
@spectree_serialize(response_model=AutocompleteResponse, api=blueprint.backoffice_web_schema)
def autocomplete_addresses() -> AutocompleteResponse:
    query_string = request.args.get("q", "").strip()

    if len(query_string) < 3:
        return AutocompleteResponse(items=[])

    # Searching for free text in address.street + postalCode + city may be slow when we have many addresses in database,
    # so another way is "experimented" here:
    # First search using API Adresse, which is optimized for any address lookup
    try:
        addresses_info = api_adresse.search_address(address=query_string, limit=NUM_RESULTS)
    except api_adresse.NoResultException:
        return AutocompleteResponse(items=[])

    # Then check results from their banId, which is indexed, so should return very quickly
    ban_ids = [address_info.id for address_info in addresses_info]
    addresses = _get_addresses_base_query().filter(geography_models.Address.banId.in_(ban_ids)).limit(NUM_RESULTS)

    return AutocompleteResponse(
        items=[AutocompleteItem(id=address.id, text=_get_address_choice_label(address)) for address in addresses]
    )
