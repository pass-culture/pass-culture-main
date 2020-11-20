from flask import jsonify
from flask import request

from pcapi.domain.postal_code.postal_code import PostalCode
from pcapi.domain.user_emails import send_user_validation_email
from pcapi.flask_app import private_api
from pcapi.models import Offerer
from pcapi.models import UserSQLEntity
from pcapi.models.user_offerer import RightsType
from pcapi.models.venue_sql_entity import create_digital_venue
from pcapi.repository import repository
from pcapi.routes.serialization import as_dict
from pcapi.utils.config import IS_INTEGRATION
from pcapi.utils.includes import USER_INCLUDES
from pcapi.utils.logger import logger
from pcapi.utils.mailing import MailServiceException
from pcapi.utils.mailing import send_raw_email
from pcapi.utils.mailing import subscribe_newsletter
from pcapi.validation.routes.users import check_valid_signup_pro


@private_api.route("/users/signup/pro", methods=["POST"])
def signup_pro():
    objects_to_save = []
    app_origin_url = request.headers.get("origin")

    check_valid_signup_pro(request)
    new_user = UserSQLEntity(from_dict=request.json)

    existing_offerer = Offerer.query.filter_by(siren=request.json["siren"]).first()

    if existing_offerer:
        user_offerer = _generate_user_offerer_when_existing_offerer(new_user, existing_offerer)
        offerer = existing_offerer
    else:
        offerer = _generate_offerer(request.json)
        user_offerer = offerer.give_rights(new_user, RightsType.editor)
        digital_venue = create_digital_venue(offerer)
        objects_to_save.extend([digital_venue, offerer])
    objects_to_save.append(user_offerer)
    new_user.canBookFreeOffers = False
    new_user.isAdmin = False
    new_user.needsToFillCulturalSurvey = False
    new_user = _set_offerer_departement_code(new_user, offerer)

    new_user.generate_validation_token()
    objects_to_save.append(new_user)

    repository.save(*objects_to_save)

    try:
        send_user_validation_email(new_user, send_raw_email, app_origin_url, is_webapp=False)
        subscribe_newsletter(new_user)
    except MailServiceException:
        logger.exception("Mail service failure")

    return jsonify(as_dict(new_user, includes=USER_INCLUDES)), 201


def _generate_user_offerer_when_existing_offerer(new_user, offerer):
    user_offerer = offerer.give_rights(new_user, RightsType.editor)
    if not IS_INTEGRATION:
        user_offerer.generate_validation_token()
    return user_offerer


def _generate_offerer(data):
    offerer = Offerer()
    offerer.populate_from_dict(data)

    if not IS_INTEGRATION:
        offerer.generate_validation_token()
    return offerer


def _set_offerer_departement_code(new_user: UserSQLEntity, offerer: Offerer) -> UserSQLEntity:
    if IS_INTEGRATION:
        new_user.departementCode = "00"
    elif offerer.postalCode is not None:
        new_user.departementCode = PostalCode(offerer.postalCode).get_departement_code()
    else:
        new_user.departementCode = "XX"  # We don't want to trigger an error on this:
        # we want the error on user
    return new_user
