from models import Deposit, EventType, ThingType, ApiErrors


def create_initial_deposit(user_to_activate):
    existing_deposits = Deposit.query.filter_by(userId=user_to_activate.id).all()
    if existing_deposits:
        error = AlreadyActivatedException()
        error.addError('user', 'Cet utilisateur a déjà crédité son pass Culture')
        raise error

    else:
        deposit = Deposit()
        deposit.amount = 500
        deposit.user = user_to_activate
        deposit.source = 'activation'
        return deposit


def check_is_activation_booking(booking):
    return booking.stock.resolvedOffer.eventOrThing.type in [str(EventType.ACTIVATION), str(ThingType.ACTIVATION)]


class AlreadyActivatedException(ApiErrors):
    pass
