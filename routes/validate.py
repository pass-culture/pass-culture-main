""" validate """

from flask import current_app as app, jsonify, request
from flask_login import login_required, current_user
from lxml.etree import LxmlError

import models
from domain.admin_emails import maybe_send_offerer_validation_email
from domain.payments import validate_transaction_file_structure, read_message_id_in_transaction_file, generate_file_checksum
from domain.user_emails import send_validation_confirmation_email, send_venue_validation_confirmation_email
from models import ApiErrors, \
    User, \
    PcObject, UserOfferer, Offerer, Venue
from models.api_errors import ResourceNotFound, ForbiddenError
from repository import user_offerer_queries, offerer_queries
from repository.payment_queries import find_transaction_checksum
from tests.validation_validate_test import check_validation_request, check_venue_found
from utils.mailing import MailServiceException
from validation.validate import check_valid_token_for_user_validation


@app.route("/validate", methods=["GET"])
def validate():
    token = request.args.get('token')

    check_validation_request(token)

    model_names = request.args.get('modelNames')

    if model_names is None:
        e = ApiErrors()
        e.addError('modelNames', 'Vous devez fournir des noms de classes')
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

    PcObject.check_and_save(*objects_to_validate)

    user_offerers = iter([obj for obj in objects_to_validate if isinstance(obj, UserOfferer)])
    user_offerer = next(user_offerers, None)

    offerers = iter([obj for obj in objects_to_validate if isinstance(obj, Offerer)])
    offerer = next(offerers, None)
    try:
        send_validation_confirmation_email(user_offerer, offerer, app.mailjet_client.send.create)
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
    PcObject.check_and_save(venue)

    try:
        send_venue_validation_confirmation_email(venue, app.mailjet_client.send.create)
    except MailServiceException as e:
        app.logger.error('Mail service failure', e)

    return "Validation effectuée", 202


@app.route("/validate/user/<token>", methods=["GET"])
def validate_user(token):
    user_to_validate = User.query.filter_by(validationToken=token).first()
    check_valid_token_for_user_validation(user_to_validate)
    user_to_validate.validationToken = None
    PcObject.check_and_save(user_to_validate)
    user_offerer = user_offerer_queries.find_first_by_user_id(user_to_validate.id)
    if user_offerer:
        offerer = offerer_queries.find_first_by_user_offerer_id(user_offerer.id)
        try:
            maybe_send_offerer_validation_email(offerer, user_offerer, app.mailjet_client.send.create)
        except MailServiceException as e:
            app.logger.error('Mail service failure', e)

    return jsonify({}), 202


@app.route('/validate/transaction', methods=['POST'])
@login_required
def certify_transaction_file_authenticity():
    if not current_user.isAdmin:
        raise ForbiddenError()

    xml_content = request.files['file'].read().decode('utf-8')
    message_id = read_message_id_in_transaction_file(xml_content)
    found_checksum = find_transaction_checksum(message_id)

    if not found_checksum:
        raise ResourceNotFound({'xml': ["L'identifiant du document XML 'MsgId' est inconnu"]})

    given_checksum = generate_file_checksum(xml_content)

    if found_checksum != given_checksum:
        raise ApiErrors({'xml': ["L'intégrité du document n'est pas validée car la somme de contrôle est invalide : %s" % given_checksum.hex()]})

    return jsonify({'checksum': given_checksum.hex()}), 200
