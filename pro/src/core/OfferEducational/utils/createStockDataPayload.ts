import { CollectiveStockCreationBodyModel } from 'apiClient/v1'

import { OfferEducationalStockFormValues } from '..'

import {
  buildBeginningDatetimeForStockPayload,
  buildBookingLimitDatetimeForStockPayload,
} from './buildDatetimesForStockPayload'

export const createStockDataPayload = (
  values: OfferEducationalStockFormValues,
  departmentCode: string,
  offerId: string
): CollectiveStockCreationBodyModel => {
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
    // @ts-expect-error string is not assignable to number
    offerId,
  }
}
