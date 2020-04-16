from datetime import datetime

from models.db import db, versioning_manager


def create_user_activity(user, table_name, verb, issued_at=datetime.utcnow):
    Activity = versioning_manager.activity_cls
    activity = Activity()
    activity.issued_at = issued_at
    activity.table_name = table_name
    activity.verb = verb
    variables = {
        'email': user.email,
        'publicName': user.publicName,
        'offerers': user.offerers,
        'departementCode': user.departementCode,
        'canBookFreeOffers': user.canBookFreeOffers,
        'isAdmin': user.isAdmin
    }
    activity.changed_data = variables

    return activity


def create_venue_activity(venue, verb, issued_at=datetime.utcnow):
    Activity = versioning_manager.activity_cls
    activity = Activity()
    activity.issued_at = issued_at
    activity.table_name = 'venue'
    activity.verb = verb
    variables = {
        'id': venue.id,
        'name': venue.name,
        'siret': venue.siret,
        'departementCode': venue.departementCode,
        'postalCode': venue.postalCode
    }
    activity.changed_data = variables

    return activity


def create_activity(table_name, verb, issued_at=datetime(2019, 1, 1), changed_data=None, old_data=None):
    Activity = versioning_manager.activity_cls
    activity = Activity()
    activity.issued_at = issued_at
    activity.table_name = table_name
    activity.verb = verb

    if changed_data:
        activity.changed_data = changed_data
    if old_data:
        activity.old_data = old_data

    return activity


def create_booking_activity(booking, table_name, verb, issued_at=datetime.utcnow, data=None):
    Activity = versioning_manager.activity_cls
    activity = Activity()
    activity.issued_at = issued_at
    activity.table_name = table_name
    activity.verb = verb

    base_data = {
        'id': booking.id,
        'token': booking.token,
        'userId': booking.userId,
        'stockId': booking.stockId,
        'isCancelled': booking.isCancelled,
        'quantity': booking.quantity,
        'recommendationId': booking.recommendationId,
        'isUsed': booking.isUsed
    }

    if verb.lower() == 'insert':
        activity.old_data = {}
        activity.changed_data = base_data
    elif verb.lower() == 'update':
        activity.old_data = base_data
        activity.changed_data = data
    elif verb.lower() == 'delete':
        activity.old_data = base_data
        activity.changed_data = {}

    return activity


def create_stock_activity(stock, verb, issued_at=datetime.utcnow, data=None):
    Activity = versioning_manager.activity_cls
    activity = Activity()
    activity.issued_at = issued_at
    activity.table_name = 'stock'
    activity.verb = verb

    base_data = {
        'id': stock.id,
        'quantity': stock.quantity
    }

    if verb.lower() == 'insert':
        activity.old_data = {}
        activity.changed_data = base_data
    elif verb.lower() == 'update':
        activity.old_data = base_data
        activity.changed_data = data
    elif verb.lower() == 'delete':
        activity.old_data = base_data
        activity.changed_data = data

    return activity


def save_all_activities(*objects):
    for obj in objects:
        db.session.add(obj)
    db.session.commit()
