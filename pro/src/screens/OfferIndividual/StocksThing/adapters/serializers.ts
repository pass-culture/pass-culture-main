import endOfDay from 'date-fns/endOfDay'

import { StockCreationBodyModel, StockEditionBodyModel } from 'apiClient/v1'
import { toISOStringWithoutMilliseconds } from 'utils/date'
import { getUtcDateTimeFromLocalDepartement } from 'utils/timezone'

import { IStockThingFormValues } from '../'

const serializeThingBookingLimitDatetime = (
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
  formValues: IStockThingFormValues,
  departementCode: string
): StockCreationBodyModel[] | StockEditionBodyModel[] => {
  const apiStock: StockCreationBodyModel = {
    bookingLimitDatetime: formValues.bookingLimitDatetime
      ? serializeThingBookingLimitDatetime(
          formValues.bookingLimitDatetime,
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
    if (formValues.activationCodesExpirationDatetime) {
      apiStock.activationCodesExpirationDatetime =
        serializeThingBookingLimitDatetime(
          formValues.activationCodesExpirationDatetime,
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
