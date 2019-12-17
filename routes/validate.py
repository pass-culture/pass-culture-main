""" validate """

from flask import current_app as app, jsonify, request
from flask_login import login_required, current_user

import models
from domain.admin_emails import maybe_send_offerer_validation_email
from domain.user_emails import send_pro_user_waiting_for_validation_by_admin_email
from domain.payments import read_message_name_in_message_file, \
    generate_file_checksum
from domain.user_emails import send_validation_confirmation_email_to_pro, send_venue_validation_confirmation_email
from models import ApiErrors, \
    PcObject, UserOfferer, Offerer, Venue
from models.api_errors import ResourceNotFoundError, ForbiddenError
from repository import user_offerer_queries, offerer_queries, user_queries
from repository.payment_queries import find_message_checksum
from utils.config import IS_INTEGRATION
from utils.mailing import MailServiceException, send_raw_email
from validation.validate import check_valid_token_for_user_validation, check_validation_request, check_venue_found


@app.route("/validate", methods=["GET"])
def validate():
    token = request.args.get('token')

    check_validation_request(token)

    model_names = request.args.get('modelNames')

    if model_names is None:
        e = ApiErrors()
        e.add_error('modelNames', 'Vous devez fournir des noms de classes')
        return jsonify(e.errors), 400

    model_names = model_names.split(',')

    objects_to_validate = []
    for model_name in model_names:
        query = getattr(models, model_name) \
            .query \
            .filter_by(validationToken=token)
        objects_to_validate += query.all()

    if len(objects_to_validate) == 0:
        return "Aucun(e) objet ne correspond à ce code de validation" \
               + " ou l'objet est déjà validé", \
               404

    for obj in objects_to_validate:
        obj.validationToken = None

    PcObject.save(*objects_to_validate)

    offerers = iter([obj for obj in objects_to_validate if isinstance(obj, Offerer)])
    offerer = next(offerers, None)
    try:
        send_validation_confirmation_email_to_pro(offerer, send_raw_email)
    except MailServiceException as e:
        app.logger.error('Mail service failure', e)
    return "Validation effectuée", 202


@app.route("/validate/venue/", methods=["GET"])
def validate_venue():
    token = request.args.get('token')
    check_validation_request(token)
    venue = Venue.query.filter_by(validationToken=token).first()
    check_venue_found(venue)
    venue.validationToken = None
    PcObject.save(venue)

    try:
        send_venue_validation_confirmation_email(venue, send_raw_email)
    except MailServiceException as e:
        app.logger.error('Mail service failure', e)

    return "Validation effectuée", 202


@app.route("/validate/user/<token>", methods=["PATCH"])
def validate_user(token):
    app_origin_url = request.headers.get('origin')
    user_to_validate = user_queries.find_by_validation_token(token)
    check_valid_token_for_user_validation(user_to_validate)
    user_to_validate.validationToken = None
    PcObject.save(user_to_validate)
    user_offerer = user_offerer_queries.find_one_or_none_by_user_id(user_to_validate.id)
    if user_offerer:
        offerer = offerer_queries.find_first_by_user_offerer_id(user_offerer.id)
        if IS_INTEGRATION:
            _validate_offerer(offerer, user_offerer)
        else:
            _ask_for_validation(offerer, user_offerer)

        try:
            send_pro_user_waiting_for_validation_by_admin_email(user_to_validate, send_raw_email, offerer)
        except MailServiceException as e:
            app.logger.error('Mail service failure', e)

    return '', 204


@app.route('/validate/payment_message', methods=['POST'])
@login_required
def certify_message_file_authenticity():
    if not current_user.isAdmin:
        raise ForbiddenError()

    xml_content = request.files['file'].read().decode('utf-8')
    message_id = read_message_name_in_message_file(xml_content)
    found_checksum = find_message_checksum(message_id)

    if not found_checksum:
        raise ResourceNotFoundError({'xml': ["L'identifiant du document XML 'MsgId' est inconnu"]})

    given_checksum = generate_file_checksum(xml_content)

    if found_checksum != given_checksum:
        raise ApiErrors({'xml': [
            "L'intégrité du document n'est pas validée car la somme de contrôle est invalide : %s" % given_checksum.hex()]})

    return jsonify({'checksum': given_checksum.hex()}), 200


def _ask_for_validation(offerer: Offerer, user_offerer: UserOfferer):
    try:
        maybe_send_offerer_validation_email(offerer, user_offerer, send_raw_email)

    except MailServiceException as e:
        app.logger.error('Mail service failure', e)


def _validate_offerer(offerer: Offerer, user_offerer: UserOfferer):
    offerer.validationToken = None
    user_offerer.validationToken = None
    PcObject.save(offerer, user_offerer)
