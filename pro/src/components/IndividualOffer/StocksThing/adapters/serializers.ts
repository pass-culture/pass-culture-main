import { endOfDay } from 'date-fns'

import {
  ProductStockCreateBodyModel,
  ProductStockUpdateBodyModel,
} from 'apiClient/v1'
import {
  getYearMonthDay,
  isDateValid,
  toISOStringWithoutMilliseconds,
} from 'commons/utils/date'
import { getUtcDateTimeFromLocalDepartement } from 'commons/utils/timezone'

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

export const serializeUpdateThingStock = (
  formValues: StockThingFormValues,
  departementCode?: string | null
): ProductStockUpdateBodyModel => {
  const [
    yearBookingLimitDatetime,
    monthBookingLimitDatetime,
    dayBookingLimitDatetime,
  ] = getYearMonthDay(formValues.bookingLimitDatetime)

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
  const quantity = formValues.quantity === null || formValues.quantity === ''
  ? null
 : formValues.quantity

  return { price, bookingLimitDatetime, quantity }
}

export const serializeCreateThingStock = (
  formValues: StockThingFormValues,
  offerId: number,
  departementCode?: string | null
): ProductStockCreateBodyModel => {
  const baseStock = serializeUpdateThingStock(formValues, departementCode)

  const apiStock: ProductStockCreateBodyModel = {...baseStock,offerId }
  
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

  return apiStock
}
