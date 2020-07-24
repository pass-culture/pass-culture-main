from typing import List

from domain.beneficiary_bookings.beneficiary_bookings import BeneficiaryBookings, BeneficiaryBooking
from domain.beneficiary_bookings.beneficiary_bookings_repository import BeneficiaryBookingsRepository
from infrastructure.repository.beneficiary_bookings.stock_domain_converter import to_domain
from models import BookingSQLEntity, UserSQLEntity, StockSQLEntity, Offer, VenueSQLEntity
from models.db import db


class BeneficiaryBookingsSQLRepository(BeneficiaryBookingsRepository):
    def get_beneficiary_bookings(self, beneficiary_id: int) -> BeneficiaryBookings:
        booking_sql_entity_views = _get_bookings_information(beneficiary_id)

        offers_ids = [booking.offerId for booking in booking_sql_entity_views]
        stock_sql_entity_views = _get_stocks_information(offers_ids)

        stocks = [to_domain(stock) for stock in stock_sql_entity_views]

        beneficiary_bookings = []
        for booking in booking_sql_entity_views:
            beneficiary_bookings.append(
                BeneficiaryBooking(
                    amount=booking.amount,
                    cancellationDate=booking.cancellationDate,
                    dateCreated=booking.dateCreated,
                    dateUsed=booking.dateUsed,
                    id=booking.id,
                    isCancelled=booking.isCancelled,
                    isUsed=booking.isUsed,
                    quantity=booking.quantity,
                    recommendationId=booking.recommendationId,
                    stockId=booking.stockId,
                    token=booking.token,
                    userId=booking.userId,
                    offerId=booking.offerId,
                    name=booking.name,
                    type=booking.type,
                    url=booking.url,
                    email=booking.email,
                    beginningDatetime=booking.beginningDatetime,
                    venueId=booking.venueId,
                    departementCode=booking.departementCode,
                    withdrawalDetails=booking.withdrawalDetails,
                    isDuo=booking.isDuo,
                    extraData=booking.extraData,
                    durationMinutes=booking.durationMinutes,
                    description=booking.description,
                    isNational=booking.isNational,
                    mediaUrls=booking.mediaUrls,
                    venueName=booking.venueName,
                    address=booking.address,
                    postalCode=booking.postalCode,
                    city=booking.city,
                    latitude=booking.latitude,
                    longitude=booking.longitude,
                    price=booking.price,
                )
            )
        return BeneficiaryBookings(bookings=beneficiary_bookings, stocks=stocks)


def _get_stocks_information(offers_ids: List[int]) -> List[object]:
    stocks_sql_entity = StockSQLEntity.query \
        .join(Offer, Offer.id == StockSQLEntity.offerId) \
        .filter(StockSQLEntity.offerId.in_(offers_ids)) \
        .with_entities(StockSQLEntity.dateCreated,
                       StockSQLEntity.beginningDatetime,
                       StockSQLEntity.bookingLimitDatetime,
                       StockSQLEntity.dateModified,
                       StockSQLEntity.offerId,
                       StockSQLEntity.quantity,
                       StockSQLEntity.price,
                       StockSQLEntity.id,
                       StockSQLEntity.isSoftDeleted,
                       Offer.isActive) \
        .all()
    return stocks_sql_entity


def _get_bookings_information(beneficiary_id: int) -> List[object]:
    offer_activation_types = ['ThingType.ACTIVATION', 'EventType.ACTIVATION']
    return db.session.query(BookingSQLEntity) \
        .join(UserSQLEntity, UserSQLEntity.id == BookingSQLEntity.userId) \
        .join(StockSQLEntity, StockSQLEntity.id == BookingSQLEntity.stockId) \
        .join(Offer) \
        .join(VenueSQLEntity) \
        .filter(BookingSQLEntity.userId == beneficiary_id) \
        .filter(Offer.type.notin_(offer_activation_types)) \
        .distinct(BookingSQLEntity.stockId) \
        .order_by(BookingSQLEntity.stockId,
                  BookingSQLEntity.isCancelled,
                  BookingSQLEntity.dateCreated.desc()
                  ) \
        .with_entities(BookingSQLEntity.amount,
                       BookingSQLEntity.cancellationDate,
                       BookingSQLEntity.dateCreated,
                       BookingSQLEntity.dateUsed,
                       BookingSQLEntity.id,
                       BookingSQLEntity.isCancelled,
                       BookingSQLEntity.isUsed,
                       BookingSQLEntity.quantity,
                       BookingSQLEntity.recommendationId,
                       BookingSQLEntity.stockId,
                       BookingSQLEntity.token,
                       BookingSQLEntity.userId,
                       Offer.id.label("offerId"),
                       Offer.name,
                       Offer.type,
                       Offer.url,
                       Offer.withdrawalDetails,
                       Offer.isDuo,
                       Offer.extraData,
                       Offer.durationMinutes,
                       Offer.description,
                       Offer.mediaUrls,
                       Offer.isNational,
                       UserSQLEntity.email,
                       StockSQLEntity.beginningDatetime,
                       StockSQLEntity.price,
                       VenueSQLEntity.id.label("venueId"),
                       VenueSQLEntity.departementCode,
                       VenueSQLEntity.name.label("venueName"),
                       VenueSQLEntity.address,
                       VenueSQLEntity.postalCode,
                       VenueSQLEntity.city,
                       VenueSQLEntity.latitude,
                       VenueSQLEntity.longitude,
                       ) \
        .all()
