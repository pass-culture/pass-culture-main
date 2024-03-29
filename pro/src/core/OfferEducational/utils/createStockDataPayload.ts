import { CollectiveStockCreationBodyModel } from 'apiClient/v1'

import { OfferEducationalStockFormValues } from '../types'

import {
  buildBeginningDatetimeForStockPayload,
  buildBookingLimitDatetimeForStockPayload,
} from './buildDatetimesForStockPayload'

export const createStockDataPayload = (
  values: OfferEducationalStockFormValues,
  departmentCode: string,
  offerId: number
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
    offerId,
  }
}
