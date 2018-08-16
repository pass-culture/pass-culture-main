from models import Booking


def find_all_by_user_id(user_id):
    return Booking.query.filter_by(userId=user_id).all()
