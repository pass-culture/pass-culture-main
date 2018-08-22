""" user mediations routes """
import csv
import os
from datetime import datetime
from inspect import isclass
from io import BytesIO, StringIO

from flask import current_app as app, jsonify, request, send_file
from sqlalchemy import func, distinct, extract

import models
from models import Booking
from models import Event
from models import EventOccurrence
from models import Offer
from models import Offerer
from models import Stock
from models import Thing
from models import User
from models import UserOfferer
from models import Venue
from models.api_errors import ApiErrors
from models.db import db
from models.pc_object import PcObject

from postgresql_audit.flask import versioning_manager

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

    query = db.session.query(User.id, Activity.issued_at, User.departementCode) \
        .join(Activity, Activity.table_name == 'users') \
        .filter(Activity.verb == 'insert')

    if department:
        query = query.filter(User.departementCode == department)
    if date_min:
        query = query.filter(Activity.issued_at >= date_min)
    if date_max:
        query = query.filter(Activity.issued_at <= date_max)

    result = query.order_by(Activity.issued_at).all()
    file_name = 'export_%s_users.csv' % datetime.utcnow().strftime('%y_%m_%d')
    headers = ['user_id', 'dateCreated', 'department']
    return _make_csv_response(file_name, headers, result)

@app.route('/exports/users_stats', methods=['GET'])
def get_users_stats():
    _check_token()
    type_date = _check_type_date(request.args.get('type_date'))

    result = db.session.query(User.departementCode, func.date_trunc(type_date, Activity.issued_at), func.count(distinct(User.id)), func.count(Booking.id), func.count(distinct(Booking.userId))) \
        .join(Activity, Activity.table_name == 'user') \
        .filter(Activity.verb == 'insert') \
        .filter(User.canBookFreeOffers == 'true') \
        .join(Booking, isouter = 'true') \
        .group_by(func.date_trunc(type_date, Activity.issued_at), User.departementCode) \
        .all()

    file_name = 'export_%s_users_stats.csv' % datetime.utcnow().strftime('%y_%m_%d')
    headers = ['department', type_date, 'distinct_user', 'count_booking', 'count_distinct_booking_users']
    return _make_csv_response(file_name, headers, result)

@app.route('/exports/bookings', methods=['GET'])
def get_bookings_per_date_per_departement():
    _check_token()
    booking_date_min = request.args.get('booking_date_min')
    booking_date_max = request.args.get('booking_date_max')
    event_date_min = request.args.get('event_date_min')
    event_date_max = request.args.get('event_date_max')
    user_department = request.args.get('user_department')
    venue_department = request.args.get('venue_department')

    query = db.session.query(User.id, User.departementCode, Booking.id, Booking.dateModified, Stock.id, EventOccurrence.id, EventOccurrence.beginningDatetime, Offer.id, Venue.id, Venue.name, Venue.departementCode, Offerer.id, Offerer.name, Event.id, Event.name) \
        .join(Booking) \
        .join(Activity, Activity.table_name == 'booking') \
        .filter(Activity.verb == 'insert') \
        .join(Stock) \
        .join(EventOccurrence) \
        .join(Offer) \
        .join(Venue) \
        .join(Offerer) \
        .join(Event)

    if booking_date_min:
        query = query.filter(Activity.issued_at >= booking_date_min)
    if booking_date_max:
        query = query.filter(Activity.issued_at <=  booking_date_max)
    if event_date_min:
        query = query.filter(EventOccurrence.beginningDatetime >= event_date_min)
    if event_date_max:
        query = query.filter(EventOccurrence.beginningDatetime <= event_date_max)
    if user_department:
        query = query.filter(User.departementCode == user_department)
    if venue_department:
        query = query.filter(Venue.departementCode == venue_department)

    result = query.all()
    file_name = 'export_%s_bookings.csv' % datetime.utcnow().strftime('%y_%m_%d')
    headers = ['User_id', 'User_departementCode', 'Booking_id', 'Booking_dateModified', 'Stock_id', 'EventOccurrence_id', 'EventOccurrence_beginningDatetime', 'Offer_id', 'Venue_id', 'Venue_name', 'Venue_departementCode', 'Offerer_id', 'Offerer_name', 'Event_id', 'Event_name']
    return _make_csv_response(file_name, headers, result)


@app.route('/exports/offers', methods=['GET'])
def get_offers_per_date_per_department():
    _check_token()
    date_min = request.args.get('date_min')
    date_max = request.args.get('date_max')
    department = request.args.get('department')

    query = db.session.query(Offer.id, Event.id, Event.name, EventOccurrence.beginningDatetime, Venue.departementCode, Offerer.id, Offerer.name) \
        .join(Event) \
        .join(EventOccurrence) \
        .join(Venue) \
        .join(Offerer)

    if department:
        query = query.filter(Venue.departementCode == department)
    if date_min:
        query = query.filter(EventOccurrence.beginningDatetime >= date_min)
    if date_max:
        query = query.filter(EventOccurrence.beginningDatetime <= date_max)

    result = query.order_by(EventOccurrence.beginningDatetime) \
        .all()
    file_name = 'export_%s_offers.csv' % datetime.utcnow().strftime('%y_%m_%d')
    headers = ['offer_id', 'event_id', 'event_name', 'event_date', 'departement_code', 'Offerer_id', 'Offerer_name']
    return _make_csv_response(file_name, headers, result)


@app.route('/exports/offerers', methods=['GET'])
def get_offerers_per_date_per_departement():
    _check_token()
    date_min = request.args.get('date_min')
    date_max = request.args.get('date_max')
    department = request.args.get('department')

    # query = db.session.query(Offerer.id, Offerer.name, Offerer.dateCreated, Venue.departementCode) \
    #     .join(Venue) \
    query = db.session.query(func.distinct(Offerer.id), Offerer.name, Activity.issued_at, Venue.departementCode) \
        .join(Venue) \
        .join(Activity, Activity.table_name == 'offerer') \
        .filter(Activity.verb == 'insert')

    # db.session.query(Offerer.name, Venue.id, Activity.issued_at).join(Venue).join(Activity, activity.table_name = %s' % Venue.__table__).all()

    if department:
        query = query.filter(Venue.departementCode == department)
    if date_min:
        query = query.filter(Activity.issued_at >= date_min)
    if date_max:
        query = query.filter(Activity.issued_at <= date_max)

    result = query.order_by(Activity.issued_at) \
        .all()

    file_name = 'export_%s_offerers.csv' % datetime.utcnow().strftime('%y_%m_%d')
    headers = ['Offerer_id', 'Offerer_name', 'dateCreated', 'departement_code']
    return _make_csv_response(file_name, headers, result)


@app.route('/exports/user_offerers', methods=['GET'])
def get_user_offerers_Offer_Book():
    _check_token()
    date_min = request.args.get('date_min')
    date_max = request.args.get('date_max')
    department = request.args.get('department')

    # query = db.session.query(User.id, UserOfferer.rights, User.dateCreated, User.email, Offerer.id, Offerer.name, Venue.id, Venue.departementCode, Venue.name, Offer.id, Offer.dateCreated, Booking.id, Booking.dateModified) \
    #     .join(UserOfferer) \
    #     .join(Offerer, isouter = True) \
    #     .join(Venue) \
    #     .join(Offer, isouter = True) \
    #     .join(Stock) \
    #     .join(Booking, isouter = True) \


    query = db.session.query(Offerer.id, Offerer.name, Venue.id, Venue.departementCode, Venue.name, Offer.id, Offer.dateCreated, Event.id, Event.name, Stock.id, Booking.id, Booking.dateModified) \
        .join(Venue) \
        .join(Offer, isouter = True) \
        .join(Stock, isouter = True) \
        .join(Booking, isouter = True) \
        .join(Event)

        
    # query = db.session.query(Offerer.id, Offerer.name, Venue.id, Venue.departementCode, Venue.name, Offer.id, Offer.dateCreated, Event.id, Event.name, Stock.id, Booking.id, Booking.dateModified) \
    #     .join(Venue) \
    #     .outerjoin(Offer)
    #     .outerjoin(Stock)
    #     .outerjoin(Booking) \
    #     .join(Event)

    if department:
        query = query.filter(Venue.departementCode == department)
    if date_min:
        query = query.filter(Offerer.dateCreated >= date_min)
    if date_max:
        query = query.filter(Offerer.dateCreated <= date_max)

    result = query.all()

    file_name = 'export_%s_userOfferers.csv' % datetime.utcnow().strftime('%y_%m_%d')
    headers = ['Offerer_id', 'Offerer_name', 'Venue_id', 'Venue_departementCode', 'Venue_name', 'Offer_id', 'Offer_dateCreated', 'Event_id', 'Event_name', 'Stock.id', 'Booking_id', 'Booking_dateModified']
    # headers = ['User_id', 'UserOfferer_rights', 'User_dateCreated', 'User_email', 'Offerer_id', 'Offerer_name', 'Venue_id', 'Venue_departementCode', 'Venue_name', 'Offer_id', 'Offer_dateCreated', 'Event_id', 'Event_name', 'Thing_id', 'Thing_name', 'Booking_id', 'Booking_dateModified']
    return _make_csv_response(file_name, headers, result)


@app.route('/exports/venue_per_department', methods=['GET'])
def get_venue_per_department():
    _check_token()

    result = db.session.query(Venue.departementCode, func.count(Venue.id)) \
        .group_by(Venue.departementCode) \
        .order_by(Venue.departementCode) \
        .all()

    file_name = 'export_%s_venue_per_department.csv' % datetime.utcnow().strftime('%y_%m_%d')
    headers = ['departement_code', 'nb_Venue']
    return _make_csv_response(file_name, headers, result)


@app.route('/exports/tracked_activity', methods=['GET'])
def get_tracked_activity_from_id():
    _check_token()
    object_id = request.args.get('object_id')
    table_name = request.args.get('table_name')

    result = db.session.query(Activity.changed_data) \
        .filter(Activity.table_name == table_name, 
        Activity.data['id'].astext.cast(db.Integer) == object_id) \
        .all()

    file_name = 'export_%s_tracked_activity.csv' % datetime.utcnow().strftime('%y_%m_%d')
    headers = []
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


def _check_type_date(type_date):
    if type_date == 'year' or type_date == 'month' or type_date == 'day':
        return type_date
    return 'day'