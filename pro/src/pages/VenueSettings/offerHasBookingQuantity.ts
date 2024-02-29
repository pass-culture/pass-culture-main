import {
  ListOffersOfferResponseModel,
  ListOffersStockResponseModel,
} from 'apiClient/v1'

export const offerHasBookingQuantity = (
  offers?: ListOffersOfferResponseModel[]
) => offers?.some((offer) => stocksHasBookingQuantity(offer.stocks))

const stocksHasBookingQuantity = (stocks: ListOffersStockResponseModel[]) => {
  return stocks.some((stock) => {
    const currentBookingQuantity = stock?.bookingQuantity
    return currentBookingQuantity && currentBookingQuantity > 0
  })
}
