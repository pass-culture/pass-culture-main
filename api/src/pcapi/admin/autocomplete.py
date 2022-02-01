from flask_login import current_user
import pydantic
import sqlalchemy as sqla
from werkzeug.exceptions import Forbidden

import pcapi.core.offerers.models as offerers_models
from pcapi.routes.apis import private_api
from pcapi.serialization.decorator import spectree_serialize


class Select2Query(pydantic.BaseModel):
    q: str


class Select2ResponseItem(pydantic.BaseModel):
    id: int
    text: str


class Select2Response(pydantic.BaseModel):
    items: list[Select2ResponseItem]


@private_api.route("/pc/back-office/autocomplete/offerers", methods=["GET"])
@spectree_serialize(response_model=Select2Response)
def offerers(query: Select2Query) -> Select2Response:
    """Autocomplete offerers on name or SIREN."""
    if not (current_user.is_authenticated and current_user.has_admin_role):
        raise Forbidden()
    query = (
        offerers_models.Offerer.query.filter(
            sqla.or_(
                offerers_models.Offerer.name.ilike(f"%{query.q}%"),
                offerers_models.Offerer.siren.like(f"%{query.q}%"),
            )
        )
        .order_by(offerers_models.Offerer.name)
        .limit(20)
        .with_entities(
            offerers_models.Offerer.id,
            offerers_models.Offerer.name,
            offerers_models.Offerer.siren,
        )
    )
    items = [Select2ResponseItem(id=offerer_id, text=f"{name} ({siren})") for offerer_id, name, siren in query]
    return Select2Response(items=items)
