from flask_login import login_required

from pcapi.core.educational import models as educational_models
from pcapi.models import db
from pcapi.routes.apis import private_api
from pcapi.routes.serialization import national_programs as serialization
from pcapi.serialization.decorator import spectree_serialize

from . import blueprint


@private_api.route("/national-programs", methods=["GET"])
@login_required
@spectree_serialize(
    response_model=serialization.ListNationalProgramsResponseModel,
    api=blueprint.pro_private_schema,
)
def get_national_programs() -> serialization.ListNationalProgramsResponseModel:
    query = db.session.query(educational_models.NationalProgram)

    return serialization.ListNationalProgramsResponseModel(
        __root__=[serialization.NationalProgramModel(id=program.id, name=program.name) for program in query]
    )
