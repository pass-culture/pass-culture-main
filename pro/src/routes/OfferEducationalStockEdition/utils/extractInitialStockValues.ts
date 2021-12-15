import {
  DEFAULT_EAC_STOCK_FORM_VALUES,
  OfferEducationalStockFormValues,
} from 'core/OfferEducational'
import { Offer } from 'custom_types/offer'
import { getLocalDepartementDateTimeFromUtc } from 'utils/timezone'

import { StockResponse } from '../types'

export const extractInitialStockValues = (
  stock: StockResponse | null,
  offer: Offer
): OfferEducationalStockFormValues => {
  if (!stock) {
    return DEFAULT_EAC_STOCK_FORM_VALUES
  }

  return {
    eventDate:
      getLocalDepartementDateTimeFromUtc(
        stock.beginningDatetime,
        offer.venue.departementCode
      ) ?? DEFAULT_EAC_STOCK_FORM_VALUES.eventDate,
    eventTime:
      getLocalDepartementDateTimeFromUtc(
        stock.beginningDatetime,
        offer.venue.departementCode
      ) ?? DEFAULT_EAC_STOCK_FORM_VALUES.eventTime,
    numberOfPlaces:
      stock.numberOfTickets ?? DEFAULT_EAC_STOCK_FORM_VALUES.numberOfPlaces,
    totalPrice: stock.price,
    bookingLimitDatetime:
      getLocalDepartementDateTimeFromUtc(stock.bookingLimitDatetime) ??
      DEFAULT_EAC_STOCK_FORM_VALUES.bookingLimitDatetime,
    priceDetail:
      stock.educationalPriceDetail ?? DEFAULT_EAC_STOCK_FORM_VALUES.priceDetail,
  }
}
