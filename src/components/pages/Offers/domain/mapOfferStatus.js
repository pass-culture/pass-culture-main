import { OFFER_STATUS } from './offerStatus'

export const mapOfferStatus = (isOfferActive, stocks) => {
  if (!isOfferActive) return OFFER_STATUS.DEACTIVATED

  const hasNoStockYet = stocks.length === 0
  if (hasNoStockYet) return OFFER_STATUS.SOLD_OUT

  const isOfferExpired = stocks.every(stock =>
    stock.bookingLimitDatetime ? new Date(stock.bookingLimitDatetime).valueOf() < Date.now() : false
  )
  if (isOfferExpired) return OFFER_STATUS.EXPIRED

  const isOfferSoldOut = stocks.every(stock => stock.remainingQuantity === 0)
  if (isOfferSoldOut) return OFFER_STATUS.SOLD_OUT

  return OFFER_STATUS.ACTIVE
}
