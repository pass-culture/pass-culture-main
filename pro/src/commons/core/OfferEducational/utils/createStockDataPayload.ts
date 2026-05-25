import type { CollectiveStockCreationBodyModel } from '@/apiClient/v1/new'

import type { CollectiveOfferStockFormValues } from '../types'
import {
  buildBookingLimitDatetimeForStockPayload,
  buildDatetimeForStockPayload,
} from './buildDatetimesForStockPayload'

export const createStockDataPayload = (
  values: CollectiveOfferStockFormValues,
  departmentCode: string,
  offerId: number
): CollectiveStockCreationBodyModel => {
  if (
    !values.startDate ||
    !values.eventTime ||
    !values.numberOfTickets ||
    typeof values.totalPrice !== 'number'
  ) {
    throw Error('Missing required values')
  }

  return {
    startDatetime: buildDatetimeForStockPayload(
      values.startDate,
      values.eventTime,
      departmentCode
    ),
    endDatetime: buildDatetimeForStockPayload(
      values.endDate,
      values.eventTime,
      departmentCode
    ),
    bookingLimitDatetime: buildBookingLimitDatetimeForStockPayload(
      values.startDate,
      values.eventTime,
      values.bookingLimitDate,
      departmentCode
    ),
    totalPrice: values.totalPrice,
    numberOfTickets: values.numberOfTickets,
    educationalPriceDetail: values.educationalPriceDetail,
    offerId,
  }
}
