import { IOfferIndividual, IOfferIndividualStock } from 'core/Offers/types'

import { STOCK_EVENT_FORM_DEFAULT_VALUES } from '../constants'
import { IStockEventFormValues } from '../types'

export const buildSingleInitialValues = (stock: IOfferIndividualStock) => {
  return {
    stockId: stock.id,
    remainingQuantity: stock.remainingQuantity?.toString() || 'unlimited',
    bookingsQuantity: stock.bookingsQuantity.toString(),
    quantity: stock.quantity?.toString() || '',
    beginningDate: stock.beginningDatetime
      ? new Date(stock.beginningDatetime)
      : null,
    beginningTime: stock.beginningDatetime
      ? new Date(stock.beginningDatetime)
      : null,
    bookingLimitDatetime: stock.bookingLimitDatetime
      ? new Date(stock.bookingLimitDatetime)
      : null,
    price: stock.price.toString(),
    isDeletable: stock.isEventDeletable,
  }
}

export const buildInitialValues = (
  offer: IOfferIndividual
): { stocks: IStockEventFormValues[] } => {
  return {
    stocks:
      offer.stocks.length > 0
        ? offer.stocks.map(buildSingleInitialValues)
        : [STOCK_EVENT_FORM_DEFAULT_VALUES],
  }
}
