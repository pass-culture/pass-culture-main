""" user mediations routes """
import csv
import os
from datetime import datetime
from inspect import isclass
from io import BytesIO, StringIO

from flask import current_app as app, jsonify, request, send_file
from flask_login import current_user, login_required
from postgresql_audit.flask import versioning_manager

import models
from models.api_errors import ApiErrors
from models.pc_object import PcObject
from repository import activity_queries
from repository.booking_queries import find_bookings_stats_per_department, \
    find_bookings_in_date_range_for_given_user_or_venue_departement
from repository.offer_queries import find_offers_in_date_range_for_given_venue_departement
from repository import offerer_queries
from repository.recommendation_queries import find_recommendations_in_date_range_for_given_departement
from repository.user_queries import find_users_by_department_and_date_range, find_users_stats_per_department
from repository.venue_queries import count_venues_by_departement
from validation.exports import check_user_is_admin

from utils.includes import OFFERER_INCLUDES_FOR_ADMIN


Activity = versioning_manager.activity_cls

EXPORT_TOKEN = os.environ.get('EXPORT_TOKEN')


@app.route('/exports/models', methods=['GET'])
def list_export_urls():
    _check_token()
    return "\n".join([request.host_url + 'exports/models/' + model_name
                      + '?token=' + request.args.get('token')
                      for model_name in filter(_is_exportable, models.__all__)])


@app.route('/exports/models/<model_name>', methods=['GET'])
def export_table(model_name):
    _check_token()
    ae = ApiErrors()
    if model_name not in models.__all__:
        ae.addError('global', 'Classe inconnue : ' + model_name)
        return jsonify(ae.errors), 400

    try:
        model = getattr(models, model_name)
    except KeyError:
        ae.addError('global', 'Nom de classe incorrect : ' + model_name)
        return jsonify(ae.errors), 400

    if not _is_exportable(model_name):
        ae.addError('global', 'Classe non exportable : ' + model_name)
        return jsonify(ae.errors), 400

    objects = model.query.all()

    if len(objects) == 0:
        return "", 200

    csvfile = StringIO()
    header = _clean_dict_for_export(model_name, objects[0]._asdict()).keys()
    if model_name == 'User':
        header = list(filter(lambda h: h != 'id' and h != 'password', header))
    writer = csv.DictWriter(csvfile, header, extrasaction='ignore')
    writer.writeheader()
    for obj in objects:
        dct = _clean_dict_for_export(model_name, obj._asdict())
        writer.writerow(dct)
    csvfile.seek(0)
    mem = BytesIO()
    mem.write(csvfile.getvalue().encode('utf-8'))
    mem.seek(0)
    csvfile.close()
    return send_file(mem,
                     attachment_filename='export.csv',
                     as_attachment=True)


@app.route('/exports/users', methods=['GET'])
def get_users_per_date_per_department():
    _check_token()
    date_min = request.args.get('date_min')
    date_max = request.args.get('date_max')
    department = request.args.get('department')

    users = find_users_by_department_and_date_range(date_max, date_min, department)
    file_name = 'export_%s_users.csv' % datetime.utcnow().strftime('%y_%m_%d')
    headers = ['user_id', 'dateCreated', 'department']
    return _make_csv_response(file_name, headers, users)


@app.route('/exports/users_stats', methods=['GET'])
def get_users_stats():
    _check_token()
    date_intervall = valid_time_intervall_or_default(request.args.get('date_intervall'))

    users_stats = find_users_stats_per_department(date_intervall)

    file_name = 'export_%s_users_stats.csv' % datetime.utcnow().strftime('%y_%m_%d')
    headers = ['department', 'date_intervall', 'distinct_user']
    return _make_csv_response(file_name, headers, users_stats)


@app.route('/exports/bookings_stats', methods=['GET'])
def get_bookings_stats():
    _check_token()
    date_intervall = valid_time_intervall_or_default(request.args.get('type_date'))

    bookings_stats = find_bookings_stats_per_department(date_intervall)

    file_name = 'export_%s_users_stats.csv' % datetime.utcnow().strftime('%y_%m_%d')
    headers = ['department', 'date_intervall', 'bookings_per_venue_dpt', 'distinct_booking_user']
    return _make_csv_response(file_name, headers, bookings_stats)


@app.route('/exports/bookings', methods=['GET'])
def get_bookings_per_date_per_departement():
    _check_token()
    booking_date_min = request.args.get('booking_date_min')
    booking_date_max = request.args.get('booking_date_max')
    event_date_min = request.args.get('event_date_min')
    event_date_max = request.args.get('event_date_max')
    user_department = request.args.get('user_department')
    venue_department = request.args.get('venue_department')

    result = find_bookings_in_date_range_for_given_user_or_venue_departement(booking_date_max, booking_date_min,
                                                                             event_date_max, event_date_min,
                                                                             user_department, venue_department)
    file_name = 'export_%s_bookings.csv' % datetime.utcnow().strftime('%y_%m_%d')
    headers = ['User_id', 'User_departementCode', 'Booking_id', 'Booking_issued_at',
               'EventOccurrence_id', 'EventOccurrence_beginningDatetime', 'Venue_departementCode',
               'Offerer_id', 'Offerer_name', 'Event_id', 'Event_name', 'Activity_id']
    return _make_csv_response(file_name, headers, result)


@app.route('/exports/offers', methods=['GET'])
def get_offers_per_date_per_department():
    _check_token()
    date_min = request.args.get('date_min')
    date_max = request.args.get('date_max')
    department = request.args.get('department')

    result = find_offers_in_date_range_for_given_venue_departement(date_max, date_min, department)
    file_name = 'export_%s_offers.csv' % datetime.utcnow().strftime('%y_%m_%d')
    headers = ['offer_id', 'event_id', 'event_name', 'event_date', 'departement_code', 'Offerer_id', 'Offerer_name']
    return _make_csv_response(file_name, headers, result)


@app.route('/exports/offerers', methods=['GET'])
def get_offerers_per_date_per_departement():
    _check_token()
    date_min = request.args.get('date_min')
    date_max = request.args.get('date_max')
    department = request.args.get('department')

    result = offerer_queries.find_offerers_in_date_range_for_given_departement(date_max, date_min,
       department)

    file_name = 'export_%s_offerers.csv' % datetime.utcnow().strftime('%y_%m_%d')
    headers = ['Offerer_id', 'Offerer_name', 'dateCreated', 'departement_code']
    return _make_csv_response(file_name, headers, result)


@app.route('/exports/venue_per_department', methods=['GET'])
def get_venue_per_department():
    _check_token()

    result = count_venues_by_departement()

    file_name = 'export_%s_venue_per_department.csv' % datetime.utcnow().strftime('%y_%m_%d')
    headers = ['departement_code', 'nb_Venue']
    return _make_csv_response(file_name, headers, result)


@app.route('/exports/tracked_activity', methods=['GET'])
def get_tracked_activity_from_id():
    _check_token()
    object_id = _check_int(request.args.get('object_id'))
    table_name = request.args.get('table_name')

    result = activity_queries.find_by_id_and_table_name(object_id, table_name)

    file_name = 'export_%s_tracked_activity.csv' % datetime.utcnow().strftime('%y_%m_%d')
    headers = []
    return _make_csv_response(file_name, headers, result)


@app.route('/exports/offerers_users_offers_bookings', methods=['GET'])
def get_offerers_users_offers_bookings():
    _check_token()
    department = request.args.get('department')

    result = offerer_queries.find_offerers_with_user_venues_and_bookings_by_departement(department)
    file_name = 'export_%s_offerers_users_offers_bookings.csv' % datetime.utcnow().strftime('%y_%m_%d')
    headers = ['Offerer_name', 'UserOfferer_id', 'User_email', 'User_dateCreated',
               'Venue_departementCode','Offer_dateCreated', 'Event_name', 'Activity_issued_at',
               'Booking_dateCreated']
    return _make_csv_response(file_name, headers, result)


@app.route('/exports/recommendations', methods=['GET'])
def get_recommendations():
    _check_token()
    department = request.args.get('department')
    date_min = request.args.get('date_min')
    date_max = request.args.get('date_max')

    result = find_recommendations_in_date_range_for_given_departement(date_max, date_min, department)
    file_name = 'export_%s_recommendations.csv' % datetime.utcnow().strftime('%y_%m_%d')
    headers = ['Offer_id', 'Event_name', 'Thing_name', 'countOffer_id', 'Venue_departementCode',
               'Recommendation_isClicked', 'Recommendation_isFavorite']
    return _make_csv_response(file_name, headers, result)


@app.route('/exports/offerers_siren', methods=['GET'])
def get_all_offerers_with_managing_user_information():
    _check_token()

    result = offerer_queries.find_all_offerers_with_managing_user_information()
    file_name = 'export_%s_offerer_siren.csv' % datetime.utcnow().strftime('%y_%m_%d')
    headers = ['Offerer_id', 'Offerer_name', 'Offerer_siren','Offerer_postalCode',
               'Offerer_city','User_firstName', 'User_lastName', 'User_email', 'User_phoneNumber',
               'User.postalCode']
    return _make_csv_response(file_name, headers, result)


@app.route('/exports/offerers_siren_with_venue', methods=['GET'])
def get_all_offerers_with_managing_user_information_and_venue():
    _check_token()

    result = offerer_queries.find_all_offerers_with_managing_user_information_and_venue()
    file_name = 'export_%s_offerers_siren_with_venue.csv' % datetime.utcnow().strftime('%y_%m_%d')
    headers = ['Offerer_id', 'Offerer_name', 'Offerer_siren', 'Offerer_postalCode', 'Offerer_city',
               'Venue_name', 'Venue.bookingEmail', 'Venue_postalCode', 'User_firstName',
               'User_lastName', 'User_email', 'User_phoneNumber', 'User.postalCode']
    return _make_csv_response(file_name, headers, result)


@app.route('/exports/offerers_siren_with_not_virtual_venue', methods=['GET'])
def get_all_offerers_with_managing_user_information_and_not_virtual_venue():
    _check_token()

    result = offerer_queries.find_all_offerers_with_managing_user_information_and_not_virtual_venue()
    file_name = 'export_%s_offerers_siren_with_not_virtual_venue.csv' % datetime.utcnow().strftime('%y_%m_%d')
    headers = ['Offerer_id', 'Offerer_name', 'Offerer_siren', 'Offerer_postalCode', 'Offerer_city',
               'Venue_name', 'Venue.bookingEmail', 'Venue_postalCode', 'User_firstName',
               'User_lastName', 'User_email', 'User_phoneNumber', 'User.postalCode'] 
    return _make_csv_response(file_name, headers, result)


@app.route('/exports/offerers_with_venue', methods=['GET'])
def get_all_offerers_with_venue():
    _check_token()

    result = offerer_queries.find_all_offerers_with_venue()
    file_name = 'export_%s_offerers_with_venue_venue.csv' % datetime.utcnow().strftime('%y_%m_%d')
    headers = ['Offerer_id', 'Offerer_name', 'Venue_id', 'Venue_name', 'Venue_bookingEmail',
               'Venue_postalCode', 'Venue_isVirtual'] 
    return _make_csv_response(file_name, headers, result)


@app.route('/exports/pending_validation', methods=['GET'])
@login_required
def get_pending_validation():
    check_user_is_admin(current_user)
    result = []    
    offerers = offerer_queries.find_all_pending_validation()

    for o in offerers:
        result.append(o._asdict(include=OFFERER_INCLUDES_FOR_ADMIN))

    return jsonify(result), 200


def _make_csv_response(file_name, headers, result):
    csv_file = StringIO()
    csv_writer = csv.writer(csv_file)
    csv_writer.writerow(headers)
    csv_writer.writerows(result)
    csv_file.seek(0)
    mem = BytesIO()
    mem.write(csv_file.getvalue().encode('utf-8'))
    mem.seek(0)
    csv_file.close()
    return send_file(mem, attachment_filename=file_name, as_attachment=True)


def _check_token():
    if EXPORT_TOKEN is None or EXPORT_TOKEN == '':
        raise ValueError("Missing environment variable EXPORT_TOKEN")
    token = request.args.get('token')
    api_errors = ApiErrors()
    if token is None:
        api_errors.addError('token', 'Vous devez préciser un jeton dans l''adresse (token=XXX)')
    if not token == EXPORT_TOKEN:
        api_errors.addError('token', 'Le jeton est invalide')
    if api_errors.errors:
        raise api_errors


def _is_exportable(model_name):
    model = getattr(models, model_name)
    return not model_name == 'PcObject' \
           and isclass(model) \
           and issubclass(model, PcObject)


def _clean_dict_for_export(model_name, dct):
    if model_name == 'User':
        del (dct['password'])
        del (dct['id'])
    return dct


def valid_time_intervall_or_default(time_intervall):
    if time_intervall == 'year' or time_intervall == 'month' or time_intervall == 'week' or time_intervall == 'day':
        return time_intervall
    return 'day'


def _check_int(checked_int):
    try:
        int(checked_int)
        return checked_int
    except:
        return 0
        