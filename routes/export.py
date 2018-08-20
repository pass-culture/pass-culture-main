""" user mediations routes """
import csv
import os
from datetime import datetime
from datetime import date
from inspect import isclass
from io import BytesIO, StringIO

from flask import current_app as app, jsonify, request, send_file
from sqlalchemy import func

import models

from models import Booking
from models import Event
from models import EventOccurrence
from models import Offer
from models import Offerer
from models import Stock
from models import UserOfferer
from models import User
from models import Venue
from models.api_errors import ApiErrors
from models.db import db
from models.pc_object import PcObject

EXPORT_TOKEN = os.environ.get('EXPORT_TOKEN')


@app.route('/export/', methods=['GET'])
def list_export_urls():
    _check_token()
    return "\n".join([request.host_url + 'export/' + model_name
                      + '?token=' + request.args.get('token')
                      for model_name in filter(_is_exportable, models.__all__)])


@app.route('/export/jambon/<model_name>', methods=['GET'])
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

# User
@app.route('/export/users_per_department', methods=['GET'])
def get_users_per_department():
    _check_token()

    result = db.session.query(
        User.departementCode,
        func.count(User.id)) \
        .group_by(User.departementCode) \
        .order_by(User.departementCode) \
        .all()
    file_name = 'export_%s_users_per_department.csv' % datetime.utcnow().strftime('%y_%m_%d')
    headers = ['departement_code', 'nb_users']

    return _make_csv_response(file_name, headers, result)


@app.route('/export/users_per_date_or_per_department', methods=['GET'])
def get_users_per_date_or_per_department():
    _check_token()
    date_min = request.args.get('date_min')
    date_max = request.args.get('date_max')
    department = request.args.get('department')

    query = db.session.query(User.id, User.dateCreated, User.departementCode)

    if department:
        query = query.filter(User.departementCode == department)
    
    if date_min:
        query = query.filter(User.dateCreated >= date_min)

    if date_max:
        query = query.filter(User.dateCreated <= date_max)       

    result = query.order_by(User.dateCreated).all()
    file_name = 'export_%s_user_per_date_or_per_departement.csv' % datetime.utcnow().strftime('%y_%m_%d')
    headers = ['user_id','dateCreated','department']
    return _make_csv_response(file_name, headers, result)


@app.route('/export/userOfferers_per_rights', methods=['GET'])
def get_userOfferers_per_rights():
    _check_token()

    result = db.session.query(
        UserOfferer.rights, 
        func.count(UserOfferer.id))\
        .group_by(UserOfferer.rights) \
        .order_by(UserOfferer.rights) \
        .all() 
    file_name = 'export_%s_userOfferer_per_rights.csv' % datetime.utcnow().strftime('%y_%m_%d')
    headers = ['rigths_type', 'nb_userOfferers']

    return _make_csv_response(file_name, headers, result)


# Booking
@app.route('/export/bookings_per_users_department', methods=['GET'])
def get_bookings_per_user_departments():
    _check_token()
    
    result = db.session.query( \
        User.departementCode, \
        func.count(User.id)) \
        .join(Booking) \
        .group_by(User.departementCode) \
        .all()
    file_name = 'export_%s_Booking_per_users_department.csv' % datetime.utcnow().strftime('%y_%m_%d')
    headers = ['departement_code', 'nb_bookings']

    return _make_csv_response(file_name, headers, result)

@app.route('/export/bookings_per_users_per_department', methods=['GET'])
def get_bookings_per_user_per_departments():
    _check_token()
    
    result = db.session.query( \
        User.departementCode, \
        User.id, \
        func.count(Booking.id)) \
        .join(Booking) \
        .group_by(User.id) \
        .order_by(User.departementCode) \
        .all()

    file_name = 'export_%s_Booking_per_users_department.csv' % datetime.utcnow().strftime('%y_%m_%d')
    headers = ['departement_code', 'user_id',  'nb_bookings']

    return _make_csv_response(file_name, headers, result)

# Offer
@app.route('/export/offers_per_date_or_per_department', methods=['GET'])
def get_offers_per_date_or_per_department():
    _check_token()
    date_min = request.args.get('date_min')
    date_max = request.args.get('date_max')
    department = request.args.get('department')

    query = db.session.query(Offer.id, Event.id, Event.name, EventOccurrence.beginningDatetime, Venue.departementCode) \
        .join(Event) \
        .join(EventOccurrence) \
        .join(Venue)

    if department:
        query = query.filter(Venue.departementCode == department)
    if date_min:
        query = query.filter(EventOccurrence.beginningDatetime >= date_min)
    if date_max:
        query = query.filter(EventOccurrence.beginningDatetime <= date_max)

    result = query.order_by(EventOccurrence.beginningDatetime) \
        .all()

    file_name = 'export_%s_Offers_per_date_or_per_department.csv' % datetime.utcnow().strftime('%y_%m_%d')
    headers = ['offer_id','event_id', 'event_name', 'event_date', 'departement_code' ]
    return _make_csv_response(file_name, headers, result)

# Offerer
@app.route('/export/offerers_per_date_or_per_departement', methods=['GET'])
def get_offerers_per_date_or_per_departement():
    _check_token()    
    date_min = request.args.get('date_min')
    date_max = request.args.get('date_max')
    department = request.args.get('department')

    query = db.session.query(Offerer.id, Offerer.name, Offerer.dateCreated, Venue.departementCode) \
        .join(Venue)

    if department:
        query = query.filter(Venue.departementCode == department)
    if date_min:
        query = query.filter(Offerer.dateCreated >= date_min)
    if date_max:
        query = query.filter(Offerer.dateCreated <= date_max)

    result = query.order_by(Offerer.dateCreated) \
        .all()

    file_name = 'export_%s_offerers_per_date_or_per_department.csv' % datetime.utcnow().strftime('%y_%m_%d')
    headers = ['Offerer_id', 'Offerer_name', 'dateCreated', 'departement_code' ]
    return _make_csv_response(file_name, headers, result)

# Venue
@app.route('/export/venue_per_department', methods=['GET'])
def get_venue_per_department():
    _check_token()

    result = db.session.query(Venue.departementCode, func.count(Venue.id)) \
        .group_by(Venue.departementCode) \
        .order_by(Venue.departementCode) \
        .all() 

    file_name = 'export_%s_venue_per_department.csv' % datetime.utcnow().strftime('%y_%m_%d')
    headers = ['departement_code', 'nb_Venue']
    return _make_csv_response(file_name, headers, result)



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
