from pcapi.serialization.decorator import spectree_serialize
from pcapi.validation.routes.users_authentifications import api_key_required

from . import blueprint


@blueprint.v1_bookings_blueprint.route("/bookings", methods=["GET"])
@spectree_serialize(
    api=blueprint.v1_bookings_schema,
)
@api_key_required
def get_booking() -> None:
    pass
