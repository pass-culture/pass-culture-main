import endOfDay from 'date-fns/endOfDay'

import { StockCreationBodyModel, StockEditionBodyModel } from 'apiClient/v1'
import {
  getYearMonthDay,
  isDateValid,
  toISOStringWithoutMilliseconds,
} from 'utils/date'
import { getUtcDateTimeFromLocalDepartement } from 'utils/timezone'

import { StockThingFormValues } from '../'

export const serializeThingBookingLimitDatetime = (
  bookingLimitDatetime: Date,
  departementCode: string
) => {
  const endOfBookingLimitDayUtcDatetime = getUtcDateTimeFromLocalDepartement(
    endOfDay(bookingLimitDatetime),
    departementCode
  )
  return toISOStringWithoutMilliseconds(endOfBookingLimitDayUtcDatetime)
}

export const serializeStockThingList = (
  formValues: StockThingFormValues,
  departementCode: string
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
            yearBookingLimitDatetime,
            monthBookingLimitDatetime,
            dayBookingLimitDatetime
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
            yearActivationCodesExpirationDatetime,
            monthActivationCodesExpirationDatetime,
            dayActivationCodesExpirationDatetime
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
