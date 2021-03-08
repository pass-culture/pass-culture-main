import { isOfferFullyBooked } from './isOfferFullyBooked'
import { OFFER_STATUS } from './offerStatus'

export const computeOfferStatus = (offer, stocks) => {
  if (!offer.isActive) {
    if (offer.validation === 'REJECTED') {
      return OFFER_STATUS.REJECTED
    }

    return OFFER_STATUS.VALIDATED
  }

  if (offer.validation === 'AWAITING') return OFFER_STATUS.AWAITING

  const hasNoStockYet = stocks.length === 0
  if (hasNoStockYet) return OFFER_STATUS.SOLD_OUT

  if (offer.hasBookingLimitDatetimesPassed) return OFFER_STATUS.EXPIRED

  if (isOfferFullyBooked(stocks)) return OFFER_STATUS.SOLD_OUT

  return OFFER_STATUS.ACTIVE
}
