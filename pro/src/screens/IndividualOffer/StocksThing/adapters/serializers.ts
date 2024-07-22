import { endOfDay } from 'date-fns'

import { StockCreationBodyModel, StockEditionBodyModel } from 'apiClient/v1'
import {
  getYearMonthDay,
  isDateValid,
  toISOStringWithoutMilliseconds,
} from 'utils/date'
import { getUtcDateTimeFromLocalDepartement } from 'utils/timezone'

import { StockThingFormValues } from '../types'

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

export const serializeStockThingList = (
  formValues: StockThingFormValues,
  departementCode?: string | null
): StockCreationBodyModel[] | StockEditionBodyModel[] => {
  const [
    yearBookingLimitDatetime,
    monthBookingLimitDatetime,
    dayBookingLimitDatetime,
  ] = getYearMonthDay(formValues.bookingLimitDatetime)

  const apiStock: StockCreationBodyModel = {
    bookingLimitDatetime: isDateValid(formValues.bookingLimitDatetime)
      ? serializeThingBookingLimitDatetime(
          new Date(
            yearBookingLimitDatetime ?? 0,
            monthBookingLimitDatetime ?? 0,
            dayBookingLimitDatetime ?? 0
          ),
          departementCode
        )
      : null,
    price: formValues.price ? formValues.price : 0,
    quantity:
      formValues.quantity === null || formValues.quantity === ''
        ? null
        : formValues.quantity,
  }
  if (formValues.activationCodes.length > 0) {
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
            yearActivationCodesExpirationDatetime ?? 0,
            monthActivationCodesExpirationDatetime ?? 0,
            dayActivationCodesExpirationDatetime ?? 0
          ),
          departementCode
        )
    }
  }
  if (formValues.stockId) {
    return [
      {
        ...apiStock,
        id: formValues.stockId,
      },
    ]
  }
  return [apiStock]
}
