import { IOfferIndividual, IOfferIndividualStock } from 'core/Offers/types'
import { getLocalDepartementDateTimeFromUtc } from 'utils/timezone'

import { STOCK_EVENT_FORM_DEFAULT_VALUES } from '../constants'
import { IStockEventFormValues } from '../types'

export const buildSingleInitialValues =
  (departementCode: string) => (stock: IOfferIndividualStock) => {
    return {
      stockId: stock.id,
      remainingQuantity: stock.remainingQuantity?.toString() || 'unlimited',
      bookingsQuantity: stock.bookingsQuantity.toString(),
      quantity: stock.quantity?.toString() || '',
      beginningDate: stock.beginningDatetime
        ? getLocalDepartementDateTimeFromUtc(
            stock.beginningDatetime,
            departementCode
          )
        : null,
      beginningTime: stock.beginningDatetime
        ? getLocalDepartementDateTimeFromUtc(
            stock.beginningDatetime,
            departementCode
          )
        : null,
      bookingLimitDatetime: stock.bookingLimitDatetime
        ? getLocalDepartementDateTimeFromUtc(
            stock.bookingLimitDatetime,
            departementCode
          )
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
        ? offer.stocks.map(buildSingleInitialValues(offer.venue.departmentCode))
        : [STOCK_EVENT_FORM_DEFAULT_VALUES],
  }
}
