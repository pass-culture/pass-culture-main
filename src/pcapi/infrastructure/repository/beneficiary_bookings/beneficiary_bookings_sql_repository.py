from pcapi.core.offers.models import Mediation
from pcapi.core.users.models import User
from pcapi.domain.beneficiary_bookings.beneficiary_booking import BeneficiaryBooking
from pcapi.domain.beneficiary_bookings.beneficiary_bookings_repository import BeneficiaryBookingsRepository
from pcapi.domain.beneficiary_bookings.beneficiary_bookings_with_stocks import BeneficiaryBookingsWithStocks
from pcapi.infrastructure.repository.beneficiary_bookings import active_mediation_domain_converter
from pcapi.infrastructure.repository.beneficiary_bookings import stock_domain_converter
from pcapi.models import ActivationCode
from pcapi.models import Booking
from pcapi.models import Offer
from pcapi.models import Product
from pcapi.models import Stock
from pcapi.models import Venue


class BeneficiaryBookingsSQLRepository(BeneficiaryBookingsRepository):
    def get_beneficiary_bookings(self, beneficiary_id: int) -> BeneficiaryBookingsWithStocks:
        booking_sql_entity_views = _get_bookings_information(beneficiary_id)

        offers_ids = [booking.offerId for booking in booking_sql_entity_views]
        stock_sql_entity_views = _get_stocks_information(offers_ids)
        mediations_sql_entity_views = _get_mediations_information(offers_ids)
        mediations = [
            active_mediation_domain_converter.to_domain(mediation) for mediation in mediations_sql_entity_views
        ]
        stocks = [stock_domain_converter.to_domain(stock) for stock in stock_sql_entity_views]

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
                    status=booking.status,
                    quantity=booking.quantity,
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
                    productId=booking.productId,
                    thumbCount=booking.thumbCount,
                    active_mediations=[mediation for mediation in mediations if mediation.offer_id == booking.offerId],
                    activationCode=booking.activationCode,
                    displayAsEnded=booking.displayAsEnded,
                )
            )
        return BeneficiaryBookingsWithStocks(bookings=beneficiary_bookings, stocks=stocks)


def _get_mediations_information(offers_ids: list[int]) -> list[object]:
    return (
        Mediation.query.join(Offer, Offer.id == Mediation.offerId)
        .filter(Mediation.offerId.in_(offers_ids))
        .filter(Mediation.isActive == True)
        .with_entities(Mediation.id, Mediation.dateCreated, Mediation.offerId)
        .all()
    )


def _get_stocks_information(offers_ids: list[int]) -> list[object]:
    return (
        Stock.query.join(Offer, Offer.id == Stock.offerId)
        .filter(Stock.offerId.in_(offers_ids))
        .with_entities(
            Stock.dateCreated,
            Stock.beginningDatetime,
            Stock.bookingLimitDatetime,
            Stock.dateModified,
            Stock.offerId,
            Stock.quantity,
            Stock.price,
            Stock.id,
            Stock.isSoftDeleted,
            Offer.isActive,
        )
        .all()
    )


def _get_bookings_information(beneficiary_id: int) -> list[Booking]:
    offer_activation_types = ["ThingType.ACTIVATION", "EventType.ACTIVATION"]
    return (
        Booking.query.join(User, User.id == Booking.userId)
        .join(Stock, Stock.id == Booking.stockId)
        .join(Offer)
        .join(Product, Offer.productId == Product.id)
        .join(Venue, Venue.id == Offer.venueId)
        .outerjoin(ActivationCode, ActivationCode.bookingId == Booking.id)
        .filter(Booking.userId == beneficiary_id)
        .filter(Offer.type.notin_(offer_activation_types))
        .distinct(Booking.stockId)
        .order_by(Booking.stockId, Booking.isCancelled, Booking.dateCreated.desc())
        .with_entities(
            Booking.amount,
            Booking.cancellationDate,
            Booking.dateCreated,
            Booking.dateUsed,
            Booking.id,
            Booking.isCancelled,
            Booking.isUsed,
            Booking.status,
            Booking.quantity,
            Booking.stockId,
            Booking.token,
            Booking.userId,
            Booking.displayAsEnded,
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
            Product.id.label("productId"),
            Product.thumbCount,
            User.email,
            Stock.beginningDatetime,
            Stock.price,
            Venue.id.label("venueId"),
            Venue.departementCode,
            Venue.name.label("venueName"),
            Venue.address,
            Venue.postalCode,
            Venue.city,
            Venue.latitude,
            Venue.longitude,
            ActivationCode.code.label("activationCode"),
        )
        .all()
    )
