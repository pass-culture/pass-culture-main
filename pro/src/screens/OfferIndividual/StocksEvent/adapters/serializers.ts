import { set } from 'date-fns'
import endOfDay from 'date-fns/endOfDay'

import { StockCreationBodyModel, StockEditionBodyModel } from 'apiClient/v1'
import { IStockEventFormValues } from 'components/StockEventForm'
import { getToday, toISOStringWithoutMilliseconds } from 'utils/date'
import { getUtcDateTimeFromLocalDepartement } from 'utils/timezone'

const serializeBookingLimitDatetime = (
  beginningDate: Date,
  beginningTime: Date,
  bookingLimitDatetime: Date,
  departementCode: string
) => {
  // If the bookingLimitDatetime is the same day as the start of the event
  // the bookingLimitDatetime should be set to beginningDate and beginningTime
  // ie : bookable until the event
  if (beginningDate.toDateString() === bookingLimitDatetime.toDateString()) {
    return serializeBeginningDateTime(
      beginningDate,
      beginningTime,
      departementCode
    )
  }
  const endOfBookingLimitDayUtcDatetime = getUtcDateTimeFromLocalDepartement(
    endOfDay(bookingLimitDatetime),
    departementCode
  )
  return toISOStringWithoutMilliseconds(endOfBookingLimitDayUtcDatetime)
}

const buildDateTime = (date: Date, time: Date) =>
  set(date, {
    hours: time.getHours(),
    minutes: time.getMinutes(),
  })

export const serializeBeginningDateTime = (
  beginningDate: Date,
  beginningTime: Date,
  departementCode: string
): string => {
  const beginningDateTimeInDepartementTimezone = buildDateTime(
    beginningDate,
    beginningTime
  )
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

  const serializedbeginningDatetime = serializeBeginningDateTime(
    formValues.beginningDate,
    formValues.beginningTime,
    departementCode
  )
  const apiStock: StockCreationBodyModel = {
    beginningDatetime: serializedbeginningDatetime,
    bookingLimitDatetime: formValues.bookingLimitDatetime
      ? serializeBookingLimitDatetime(
          formValues.beginningDate,
          formValues.beginningTime,
          formValues.bookingLimitDatetime,
          departementCode
        )
      : serializedbeginningDatetime,
    price: formValues.price || 0,
    quantity:
      formValues.quantity === null || formValues.quantity === ''
        ? null
        : formValues.quantity,
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
    .filter(stockFormValues => {
      const beginingDatetime =
        stockFormValues.beginningDate && stockFormValues.beginningTime
          ? buildDateTime(
              stockFormValues.beginningDate,
              stockFormValues.beginningTime
            )
          : null
      return beginingDatetime === null || beginingDatetime >= today
    })
    .map((formValues: IStockEventFormValues) =>
      serializeStockEvent(formValues, departementCode)
    )
}
