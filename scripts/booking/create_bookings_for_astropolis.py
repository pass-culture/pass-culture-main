from typing import List

from domain.booking.booking import Booking
from domain.client_exceptions import ClientError
from domain.expenses import get_expenses
from domain.stock.stock_validator import check_stock_is_bookable, check_expenses_limits
from infrastructure.repository.beneficiary.beneficiary_sql_repository import BeneficiarySQLRepository
from infrastructure.repository.booking.booking_sql_repository import BookingSQLRepository
from infrastructure.repository.stock.stock_sql_repository import StockSQLRepository
from models import BookingSQLEntity, StockSQLEntity, OfferSQLEntity, UserSQLEntity, ApiErrors
from utils.logger import logger


def create_bookings_for_astropolis(offer_one_id: int, offer_two_id: int, offer_three_id: int) -> None:
    stock_offer_three = StockSQLEntity.query.filter(StockSQLEntity.offerId == offer_three_id).first()

    beneficiaries_who_have_booked_offer_one = UserSQLEntity.query \
        .join(BookingSQLEntity) \
        .join(StockSQLEntity) \
        .join(OfferSQLEntity) \
        .filter(OfferSQLEntity.id == offer_one_id) \
        .filter(BookingSQLEntity.isCancelled == False) \
        .filter(StockSQLEntity.price == 0) \
        .with_entities(UserSQLEntity.id) \
        .all()
    beneficiaries_who_have_booked_offer_two = _find_beneficiaries_for_offer(offer_id=offer_two_id)
    beneficiaries_who_have_booked_offer_three = _find_beneficiaries_for_offer(offer_id=offer_three_id)

    beneficiary_ids_for_booking_creation = []
    for beneficiary_id in beneficiaries_who_have_booked_offer_one:
        if not (beneficiary_id in beneficiaries_who_have_booked_offer_two or beneficiary_id in beneficiaries_who_have_booked_offer_three):
            beneficiary_ids_for_booking_creation.append(beneficiary_id)

    if len(beneficiary_ids_for_booking_creation) > 0:
        beneficiary_sql_repository = BeneficiarySQLRepository()
        booking_sql_repository = BookingSQLRepository()
        stock_sql_repository = StockSQLRepository()

        number_of_created_bookings = 0
        beneficiary_id_in_errors = []
        for beneficiary_id in beneficiary_ids_for_booking_creation:
            beneficiary = beneficiary_sql_repository.find_beneficiary_by_user_id(user_id=beneficiary_id)
            stock = stock_sql_repository.find_stock_by_id(stock_id=stock_offer_three.id)
            expenses = booking_sql_repository.get_expenses_by_user_id(user_id=beneficiary_id)

            try:
                new_booking = Booking(beneficiary=beneficiary, stock=stock, amount=stock.price, quantity=1,
                                      is_used=True)
                check_expenses_limits(expenses, new_booking)
                booking_sql_repository.save(new_booking)
                logger.info(f'[FIX-BOOKINGS] Created booking for user {beneficiary.identifier}')

                booking_on_offer_one = booking_sql_repository.find_not_cancelled_booking_by(
                    offer_id=offer_one_id,
                    user_id=beneficiary_id
                )
                booking_on_offer_one.isCancelled = True
                booking_sql_repository.save(booking_on_offer_one)
                logger.info(
                    f'[FIX-BOOKINGS] Cancelled booking {booking_on_offer_one.identifier} '
                    f'for user {beneficiary.identifier}'
                )
                number_of_created_bookings += 1
            except ClientError:
                logger.error(f'[FIX-BOOKINGS] ClientError when trying to create booking for user {beneficiary_id}')
                logger.error(f'[FIX-BOOKINGS] Expenses {expenses}')
                beneficiary_id_in_errors.append(beneficiary_id)
            except ApiErrors:
                logger.error(f'[FIX-BOOKINGS] APIErrors, when trying to create booking for user {beneficiary_id}')
                logger.error(f'[FIX-BOOKINGS] Expenses {expenses}')
                beneficiary_id_in_errors.append(beneficiary_id)
        logger.info(f'Created {number_of_created_bookings} bookings')
        logger.info(f'Beneficiaries in error {beneficiary_id_in_errors}')


def _find_beneficiaries_for_offer(offer_id: int) -> List[int]:
    return UserSQLEntity.query \
        .join(BookingSQLEntity) \
        .join(StockSQLEntity) \
        .join(OfferSQLEntity) \
        .filter(OfferSQLEntity.id == offer_id) \
        .with_entities(UserSQLEntity.id) \
        .all()
