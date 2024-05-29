import { CollectiveStockCreationBodyModel } from 'apiClient/v1'

import { OfferEducationalStockFormValues } from '../types'

import {
  buildStartDatetimeForStockPayload,
  buildBookingLimitDatetimeForStockPayload,
  buildEndDatetimeForStockPayload,
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
    startDatetime: buildStartDatetimeForStockPayload(
      values.startDatetime,
      values.eventTime,
      departmentCode
    ),
    endDatetime: buildEndDatetimeForStockPayload(
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
