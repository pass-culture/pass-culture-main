from flask import request
import sqlalchemy as sa

from pcapi.core.offerers import models as offerers_models
from pcapi.routes.serialization import BaseModel
from pcapi.serialization.decorator import spectree_serialize

from . import blueprint


NUM_RESULTS = 20


class AutocompleteItem(BaseModel):
    id: int
    text: str


class AutocompleteResponse(BaseModel):
    items: list[AutocompleteItem]


@blueprint.backoffice_v3_web.route("/autocomplete/offerers", methods=["GET"])
@spectree_serialize(response_model=AutocompleteResponse, api=blueprint.backoffice_v3_web_schema)
def autocomplete_offerers() -> AutocompleteResponse:
    query_string = request.args.get("q", "").strip()

    if len(query_string) < 2:
        return AutocompleteResponse(items=[])

    filters = offerers_models.Offerer.name.ilike(f"%{query_string}%")

    if query_string.isnumeric() and len(query_string) <= 9:
        filters = sa.or_(filters, offerers_models.Offerer.siren.like(f"{query_string}%"))

    offerers = (
        offerers_models.Offerer.query.filter(filters)
        .limit(NUM_RESULTS)
        .with_entities(
            offerers_models.Offerer.id,
            offerers_models.Offerer.name,
            offerers_models.Offerer.siren,
        )
    )

    return AutocompleteResponse(
        items=[AutocompleteItem(id=offerer_id, text=f"{name} ({siren})") for offerer_id, name, siren in offerers]
    )


@blueprint.backoffice_v3_web.route("/autocomplete/venues", methods=["GET"])
@spectree_serialize(response_model=AutocompleteResponse, api=blueprint.backoffice_v3_web_schema)
def autocomplete_venues() -> AutocompleteResponse:
    query_string = request.args.get("q", "").strip()

    if not query_string or len(query_string) < 2:
        return AutocompleteResponse(items=[])

    filters = offerers_models.Venue.name.ilike(f"%{query_string}%")

    if query_string.isnumeric() and len(query_string) <= 14:
        filters = sa.or_(filters, offerers_models.Venue.siret.like(f"{query_string}%"))

    venues = (
        offerers_models.Venue.query.filter(filters)
        .limit(NUM_RESULTS)
        .with_entities(
            offerers_models.Venue.id,
            offerers_models.Venue.name,
            offerers_models.Venue.siret,
        )
    )

    return AutocompleteResponse(
        items=[
            AutocompleteItem(id=venue_id, text=f"{name} ({siret or 'Pas de SIRET'})")
            for venue_id, name, siret in venues
        ]
    )
