from typing import List

from sqlalchemy import func

from domain.beneficiary_bookings.beneficiary_bookings import BeneficiaryBookings, BeneficiaryBooking
from domain.beneficiary_bookings.beneficiary_bookings_repository import BeneficiaryBookingsRepository
from infrastructure.repository.beneficiary_bookings.stock_domain_converter import to_domain
from models import BookingSQLEntity, UserSQLEntity, StockSQLEntity, Offer, VenueSQLEntity
from models.db import db
from repository.offer_queries import _build_bookings_quantity_subquery


class BeneficiaryBookingsSQLRepository(BeneficiaryBookingsRepository):
    def get_beneficiary_bookings(self, beneficiary_id: int) -> BeneficiaryBookings:
        bookings_view = self._get_bookings_information(beneficiary_id)

        offers_ids = [bv.offerId for bv in bookings_view]
        stocks_sql_entity_views = self._get_stocks_information(offers_ids)

        stocks = [to_domain(stock_sql_entity) for stock_sql_entity in stocks_sql_entity_views]

        beneficiary_bookings = []
        for booking_view in bookings_view:
            beneficiary_bookings.append(
                BeneficiaryBooking(
                    amount=booking_view.amount,
                    cancellationDate=booking_view.cancellationDate,
                    dateCreated=booking_view.dateCreated,
                    dateUsed=booking_view.dateUsed,
                    id=booking_view.id,
                    isCancelled=booking_view.isCancelled,
                    isUsed=booking_view.isUsed,
                    quantity=booking_view.quantity,
                    recommendationId=booking_view.recommendationId,
                    stockId=booking_view.stockId,
                    token=booking_view.token,
                    userId=booking_view.userId,
                    offerId=booking_view.offerId,
                    name=booking_view.name,
                    type=booking_view.type,
                    url=booking_view.url,
                    email=booking_view.email,
                    beginningDatetime=booking_view.beginningDatetime,
                    venueId=booking_view.venueId,
                    departementCode=booking_view.departementCode,
                    withdrawalDetails=booking_view.withdrawalDetails,
                    isDuo=booking_view.isDuo,
                    extraData=booking_view.extraData,
                    durationMinutes=booking_view.durationMinutes,
                    description=booking_view.description,
                    isNational=booking_view.isNational,
                    mediaUrls=booking_view.mediaUrls,
                    venueName=booking_view.venueName,
                    address=booking_view.address,
                    postalCode=booking_view.postalCode,
                    city=booking_view.city,
                    latitude=booking_view.latitude,
                    longitude=booking_view.longitude,
                    price=booking_view.price,
                    stocks=[stock for stock in stocks if stock.offerId == booking_view.offerId],
                )
            )
        return BeneficiaryBookings(bookings=beneficiary_bookings, stocks=stocks)

    def _get_stocks_information(self, offers_ids: List[int]) -> List[object]:
        bookings_quantity = _build_bookings_quantity_subquery()
        stocks_sql_entity = StockSQLEntity.query \
            .join(Offer, Offer.id == StockSQLEntity.offerId) \
            .filter(StockSQLEntity.offerId.in_(offers_ids)) \
            .outerjoin(bookings_quantity, StockSQLEntity.id == bookings_quantity.c.stockId) \
            .with_entities(StockSQLEntity.dateCreated,
                           StockSQLEntity.beginningDatetime,
                           StockSQLEntity.bookingLimitDatetime,
                           StockSQLEntity.offerId,
                           StockSQLEntity.dateModified,
                           StockSQLEntity.quantity,
                           StockSQLEntity.price,
                           StockSQLEntity.id,
                           StockSQLEntity.isSoftDeleted,
                           Offer.isActive,
                           (StockSQLEntity.quantity - func.coalesce(bookings_quantity.c.quantity, 0)).label(
                               'remainingQuantity')) \
            .all()
        return stocks_sql_entity

    def _get_bookings_information(self, beneficiary_id: int) -> List[object]:
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
                           UserSQLEntity.email,
                           StockSQLEntity.beginningDatetime,
                           StockSQLEntity.price,
                           VenueSQLEntity.id.label("venueId"),
                           VenueSQLEntity.departementCode,
                           Offer.withdrawalDetails,
                           Offer.isDuo,
                           Offer.extraData,
                           Offer.durationMinutes,
                           Offer.description,
                           Offer.mediaUrls,
                           Offer.isNational,
                           VenueSQLEntity.name.label("venueName"),
                           VenueSQLEntity.address,
                           VenueSQLEntity.postalCode,
                           VenueSQLEntity.city,
                           VenueSQLEntity.latitude,
                           VenueSQLEntity.longitude,
                           ) \
            .all()
