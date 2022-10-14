import { CollectiveStockCreationBodyModel } from 'apiClient/v1'

import { OfferEducationalStockFormValues } from '../types'

import {
  buildBeginningDatetimeForStockPayload,
  buildBookingLimitDatetimeForStockPayload,
} from './buildDatetimesForStockPayload'

export const createStockDataPayload = (
  values: OfferEducationalStockFormValues,
  departementCode: string,
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
      departementCode
    ),
    bookingLimitDatetime: buildBookingLimitDatetimeForStockPayload(
      values.eventDate,
      values.eventTime,
      values.bookingLimitDatetime,
      departementCode
    ),
    totalPrice: values.totalPrice,
    numberOfTickets: values.numberOfPlaces,
    educationalPriceDetail: values.priceDetail,
    // @ts-expect-error string is not assignable to number
    offerId,
  }
}
