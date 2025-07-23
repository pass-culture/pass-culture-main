import { GetOfferStockResponseModel } from 'apiClient/v1'
import { StocksEvent } from 'components/IndividualOffer/StocksEventCreation/form/types'

export const serializeStockEvents = (
  stocks: GetOfferStockResponseModel[]
): StocksEvent[] =>
  stocks.map((stock): StocksEvent => {
    if (
      stock.beginningDatetime === null ||
      stock.beginningDatetime === undefined ||
      stock.bookingLimitDatetime === null ||
      stock.bookingLimitDatetime === undefined ||
      stock.priceCategoryId === null ||
      stock.priceCategoryId === undefined ||
      stock.quantity === undefined
    ) {
      throw new Error('Error: this stock is not a stockEvent')
    }
    return {
      id: stock.id,
      beginningDatetime: stock.beginningDatetime,
      bookingLimitDatetime: stock.bookingLimitDatetime,
      priceCategoryId: stock.priceCategoryId,
      quantity: stock.quantity,
      bookingsQuantity: stock.bookingsQuantity,
      isEventDeletable: stock.isEventDeletable,
    }
  })
