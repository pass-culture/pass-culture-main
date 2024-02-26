import { ListOffersStockResponseModel } from 'apiClient/v1'
import { Offer } from 'core/Offers/types'

export const offerHasBookingQuantity = (offers?: Offer[]) =>
  offers?.some((offer) =>
    // TODO offerCustomType
    // This "as" is temporary while unwrapping the Offer custom type
    // this function is only used in the case where Offer = ListOffersOfferResponseModel
    // when the Offer type is fully unwrapped, this "as" will be removed
    stocksHasBookingQuantity(offer.stocks as ListOffersStockResponseModel[])
  )

const stocksHasBookingQuantity = (stocks: ListOffersStockResponseModel[]) => {
  return stocks.some((stock) => {
    const currentBookingQuantity = stock?.bookingQuantity
    return currentBookingQuantity && currentBookingQuantity > 0
  })
}
