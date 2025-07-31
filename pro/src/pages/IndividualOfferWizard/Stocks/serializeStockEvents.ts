import { GetOfferStockResponseModel } from 'apiClient/v1'
import { assertOrFrontendError } from 'commons/errors/assertOrFrontendError'
import { StocksEvent } from 'components/StocksEventList/StocksEventList'

export const serializeStockEvents = (
  stocks: GetOfferStockResponseModel[]
): StocksEvent[] =>
  stocks.map((stock): StocksEvent => {
    assertOrFrontendError(
      stock.beginningDatetime !== null &&
        stock.beginningDatetime !== undefined &&
        stock.bookingLimitDatetime !== null &&
        stock.bookingLimitDatetime !== undefined &&
        stock.priceCategoryId !== null &&
        stock.priceCategoryId !== undefined &&
        stock.quantity !== undefined,
      'This stock is not a stockEvent.'
    )

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
