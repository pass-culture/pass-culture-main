from models import Booking


def find_all_by_user_id(user_id):
    return Booking.query.filter_by(userId=user_id).all()


def compute_total_booking_value_of_offerer(offerer_id):
    pass
