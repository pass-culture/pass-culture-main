import { DEFAULT_EAC_STOCK_FORM_VALUES } from 'core/OfferEducationalStock/constants'
import { OfferEducationalStockFormValues } from 'core/OfferEducationalStock/types'
import { Offer } from 'custom_types/offer'
import { getLocalDepartementDateTimeFromUtc } from 'utils/timezone'

import { StockResponse } from './types'

export const extractInitialStockValues = (
  stock: StockResponse | null,
  offer: Offer | null
): OfferEducationalStockFormValues => {
  if (!stock || !offer) {
    return DEFAULT_EAC_STOCK_FORM_VALUES
  }
  console.log(stock)

  return {
    eventDate:
      getLocalDepartementDateTimeFromUtc(
        stock.beginningDatetime,
        offer.venue.departementCode
      ) || DEFAULT_EAC_STOCK_FORM_VALUES.eventDate,
    eventTime:
      getLocalDepartementDateTimeFromUtc(
        stock.beginningDatetime,
        offer.venue.departementCode
      ) || DEFAULT_EAC_STOCK_FORM_VALUES.eventTime,
    numberOfPlaces: stock.numberOfTickets,
    totalPrice: stock.price,
    bookingLimitDatetime:
      getLocalDepartementDateTimeFromUtc(stock.bookingLimitDatetime) ||
      DEFAULT_EAC_STOCK_FORM_VALUES.bookingLimitDatetime,
  }
}
