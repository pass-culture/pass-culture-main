import { OfferEducationalStockFormValues, StockPayload } from '..'
import {
  buildBeginningDatetimeForStockPayload,
  buildBookingLimitDatetimeForStockPayload,
} from './buildDatetimesForStockPayload'

export const createStockDataPayload = (
  values: OfferEducationalStockFormValues,
  departmentCode: string
): StockPayload => {
  if (
    !values.eventDate ||
    !values.eventTime ||
    !values.numberOfPlaces ||
    typeof values.totalPrice !== 'number'
  ) {
    throw Error('Missing required values')
  }

  return {
    beginningDatetime: buildBeginningDatetimeForStockPayload(
      values.eventDate,
      values.eventTime,
      departmentCode
    ),
    bookingLimitDatetime: buildBookingLimitDatetimeForStockPayload(
      values.eventDate,
      values.eventTime,
      values.bookingLimitDatetime,
      departmentCode
    ),
    totalPrice: values.totalPrice,
    numberOfTickets: values.numberOfPlaces,
    educationalPriceDetail: values.priceDetail,
  }
}
