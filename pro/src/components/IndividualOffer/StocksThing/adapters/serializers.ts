import { endOfDay } from 'date-fns'

import type { ThingStockCreateBodyModel } from '@/apiClient/v1'
import {
  getYearMonthDay,
  isDateValid,
  toISOStringWithoutMilliseconds,
} from '@/commons/utils/date'
import { getUtcDateTimeFromLocalDepartement } from '@/commons/utils/timezone'

import type { StockThingFormValues } from '../types'

export const serializeThingBookingLimitDatetime = (
  bookingLimitDatetime: Date,
  departementCode?: string | null
) => {
  const endOfBookingLimitDayUtcDatetime = getUtcDateTimeFromLocalDepartement(
    endOfDay(bookingLimitDatetime),
    departementCode
  )
  return toISOStringWithoutMilliseconds(endOfBookingLimitDayUtcDatetime)
}

type ThingStockUpdateBody = {
  bookingLimitDatetime: string | null
  price: number
  quantity: number | null
}

export const serializeUpdateThingStock = (
  formValues: StockThingFormValues,
  readOnlyFields: string[],
  departementCode?: string | null
): ThingStockUpdateBody => {
  const [
    yearBookingLimitDatetime,
    monthBookingLimitDatetime,
    dayBookingLimitDatetime,
  ] = getYearMonthDay(formValues.bookingLimitDatetime ?? '')

  const bookingLimitDatetime = isDateValid(formValues.bookingLimitDatetime)
    ? serializeThingBookingLimitDatetime(
        new Date(
          yearBookingLimitDatetime,
          monthBookingLimitDatetime,
          dayBookingLimitDatetime
        ),
        departementCode
      )
    : null
  const price = formValues.price ? formValues.price : 0
  const quantity = formValues.quantity ?? null

  const body = { price, bookingLimitDatetime, quantity }

  if (readOnlyFields.includes('bookingLimitDatetime')) {
    //  The computed bookingLimitDatetime here might be different from the existing bookingLimitDatetime when the offer was synchronized
    //  Since we are not alowed to update its value, we remove it from the body
    delete body['bookingLimitDatetime' as keyof ThingStockUpdateBody]
  }

  return body
}

export const serializeCreateThingStock = (
  formValues: StockThingFormValues,
  offerId: number,
  readOnlyFields: string[],
  departementCode?: string | null
): ThingStockCreateBodyModel => {
  const baseStock = serializeUpdateThingStock(
    formValues,
    readOnlyFields,
    departementCode
  )

  const apiStock: ThingStockCreateBodyModel = { ...baseStock, offerId }

  if ((formValues.activationCodes ?? []).length > 0) {
    apiStock.activationCodes = formValues.activationCodes
    /* istanbul ignore next */
    if (isDateValid(formValues.activationCodesExpirationDatetime)) {
      const [
        yearActivationCodesExpirationDatetime,
        monthActivationCodesExpirationDatetime,
        dayActivationCodesExpirationDatetime,
      ] = getYearMonthDay(formValues.activationCodesExpirationDatetime)

      apiStock.activationCodesExpirationDatetime =
        serializeThingBookingLimitDatetime(
          new Date(
            yearActivationCodesExpirationDatetime,
            monthActivationCodesExpirationDatetime,
            dayActivationCodesExpirationDatetime
          ),
          departementCode
        )
    }
  }

  return apiStock
}
