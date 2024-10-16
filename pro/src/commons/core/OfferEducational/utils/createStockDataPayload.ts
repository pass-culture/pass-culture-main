import { CollectiveStockCreationBodyModel } from 'apiClient/v1'

import { OfferEducationalStockFormValues } from '../types'

import {
  buildBookingLimitDatetimeForStockPayload,
  buildDatetimeForStockPayload,
} from './buildDatetimesForStockPayload'

export const createStockDataPayload = (
  values: OfferEducationalStockFormValues,
  departmentCode: string,
  offerId: number
): CollectiveStockCreationBodyModel => {
  if (
    !values.startDatetime ||
    !values.eventTime ||
    !values.numberOfPlaces ||
    typeof values.totalPrice !== 'number'
  ) {
    throw Error('Missing required values')
  }

  return {
    startDatetime: buildDatetimeForStockPayload(
      values.startDatetime,
      values.eventTime,
      departmentCode
    ),
    endDatetime: buildDatetimeForStockPayload(
      values.endDatetime,
      values.eventTime,
      departmentCode
    ),
    bookingLimitDatetime: buildBookingLimitDatetimeForStockPayload(
      values.startDatetime,
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
