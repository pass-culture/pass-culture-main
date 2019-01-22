from models import Deposit, EventType, ThingType, PcObject, ApiErrors


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
        PcObject.check_and_save(deposit)


def check_is_activation_booking(booking):
    is_on_activation_event = booking.stock.resolvedOffer.eventOrThing.type == str(EventType.ACTIVATION)
    is_on_activation_thing = booking.stock.resolvedOffer.eventOrThing.type == str(ThingType.ACTIVATION)
    return is_on_activation_event | is_on_activation_thing


class AlreadyActivatedException(ApiErrors):
    pass