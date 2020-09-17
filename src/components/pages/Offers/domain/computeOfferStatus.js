import { OFFER_STATUS } from './offerStatus'
import { isOfferFullyBooked } from './isOfferFullyBooked'

export const computeOfferStatus = (offer, stocks) => {
  if (!offer.isActive) return OFFER_STATUS.INACTIVE

  const hasNoStockYet = stocks.length === 0
  if (hasNoStockYet) return OFFER_STATUS.SOLD_OUT

  if (offer.hasBookingLimitDatetimesPassed) return OFFER_STATUS.EXPIRED

  if (isOfferFullyBooked(stocks)) return OFFER_STATUS.SOLD_OUT

  return OFFER_STATUS.ACTIVE
}
