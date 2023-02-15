import { Offer, Stock } from 'core/Offers/types'

export const offerHasBookingQuantity = (offers?: Offer[]) =>
  offers?.some(offer => stocksHasBookingQuantity(offer.stocks))

const stocksHasBookingQuantity = (stocks: Stock[]) => {
  return stocks.some(stock => {
    const currentBookingQuantity = stock?.bookingQuantity
    return currentBookingQuantity && currentBookingQuantity > 0
  })
}
