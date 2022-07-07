from sqlalchemy.orm.exc import NoResultFound

from pcapi.core.users.models import User
from pcapi.models import Model
from pcapi.models.api_errors import ApiErrors
from pcapi.utils.human_ids import dehumanize


def check_user_has_access_to_offerer(user: User, offerer_id: int) -> None:
    if not user.has_access(offerer_id):
        raise ApiErrors(
            errors={
                "global": ["Vous n'avez pas les droits d'accès suffisant pour accéder à cette information."],
            },
            status_code=403,
        )


def load_or_404(obj_class: Model, human_id: str) -> Model:  # type: ignore [valid-type]
    return obj_class.query.get_or_404(dehumanize(human_id))  # type: ignore [attr-defined]


def load_or_raise_error(obj_class: Model, human_id: str) -> Model:  # type: ignore [valid-type]
    try:
        data = obj_class.query.filter_by(id=dehumanize(human_id)).one()  # type: ignore [attr-defined]
    except NoResultFound:
        raise ApiErrors(
            errors={
                "global": ["Aucun objet ne correspond à cet identifiant dans notre base de données"],
            },
            status_code=404,
        )
    return data
