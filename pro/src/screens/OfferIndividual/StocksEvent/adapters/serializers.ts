import { set } from 'date-fns'
import endOfDay from 'date-fns/endOfDay'
import startOfDay from 'date-fns/startOfDay'

import { StockCreationBodyModel, StockEditionBodyModel } from 'apiClient/v1'
import { IStockEventFormValues } from 'components/StockEventForm'
import { getToday, toISOStringWithoutMilliseconds } from 'utils/date'
import { getUtcDateTimeFromLocalDepartement } from 'utils/timezone'

const serializeBookingLimitDatetime = (
  bookingLimitDatetime: Date,
  departementCode: string
) => {
  const endOfBookingLimitDayUtcDatetime = getUtcDateTimeFromLocalDepartement(
    endOfDay(bookingLimitDatetime),
    departementCode
  )
  return toISOStringWithoutMilliseconds(
    startOfDay(endOfBookingLimitDayUtcDatetime)
  )
}

export const serializeBeginningDateTime = (
  beginningDate: Date,
  beginningTime: Date,
  departementCode: string
): string => {
  const beginningDateTimeInDepartementTimezone = set(beginningDate, {
    hours: beginningTime.getHours(),
    minutes: beginningTime.getMinutes(),
  })
  const beginningDateTimeInUTCTimezone = getUtcDateTimeFromLocalDepartement(
    beginningDateTimeInDepartementTimezone,
    departementCode
  )
  return toISOStringWithoutMilliseconds(beginningDateTimeInUTCTimezone)
}

export const serializeStockEvent = (
  formValues: IStockEventFormValues,
  departementCode: string
): StockCreationBodyModel | StockEditionBodyModel => {
  if (!(formValues.beginningDate instanceof Date)) {
    throw Error("La date de début d'évenement est invalide")
  }
  if (!(formValues.beginningTime instanceof Date)) {
    throw Error("L'heure de début d'évenement est invalide")
  }
  const serializedQuantity = parseInt(formValues.quantity, 10)
  const serializedbeginningDatetime = serializeBeginningDateTime(
    formValues.beginningDate,
    formValues.beginningTime,
    departementCode
  )
  const apiStock: StockCreationBodyModel = {
    beginningDatetime: serializedbeginningDatetime,
    bookingLimitDatetime: formValues.bookingLimitDatetime
      ? serializeBookingLimitDatetime(
          formValues.bookingLimitDatetime,
          departementCode
        )
      : serializedbeginningDatetime,
    price: parseInt(formValues.price, 10),
    quantity: isNaN(serializedQuantity) ? null : serializedQuantity,
  }
  if (formValues.stockId) {
    return {
      ...apiStock,
      humanizedId: formValues.stockId,
    }
  }
  return apiStock
}

export const serializeStockEventList = (
  formValuesList: IStockEventFormValues[],
  departementCode: string
): StockCreationBodyModel[] | StockEditionBodyModel[] => {
  const today = getToday()
  return formValuesList
    .filter(
      stockFormValues =>
        !stockFormValues.beginningDate || stockFormValues.beginningDate >= today
    )
    .map((formValues: IStockEventFormValues) =>
      serializeStockEvent(formValues, departementCode)
    )
}
