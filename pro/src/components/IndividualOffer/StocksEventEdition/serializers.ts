import { endOfDay } from 'date-fns'

import { EventStockUpdateBodyModel } from 'apiClient/v1'
import {
  getToday,
  isDateValid,
  toISOStringWithoutMilliseconds,
} from 'commons/utils/date'
import { getUtcDateTimeFromLocalDepartement } from 'commons/utils/timezone'
import { StockEventFormValues } from 'components/IndividualOffer/StocksEventEdition/StockFormList/types'

export const serializeBookingLimitDatetime = (
  beginningDate: string,
  beginningTime: string,
  bookingLimitDatetime: string,
  departementCode?: string | null
) => {
  // If the bookingLimitDatetime is the same day as the start of the event
  // the bookingLimitDatetime should be set to beginningDate and beginningTime
  // ie : bookable until the event
  if (
    new Date(beginningDate).toDateString() ===
    new Date(bookingLimitDatetime).toDateString()
  ) {
    return serializeDateTimeToUTCFromLocalDepartment(
      beginningDate,
      beginningTime,
      departementCode
    )
  }
  const [year, month, day] = bookingLimitDatetime.split('-')
  const endOfBookingLimitDayUtcDatetime = getUtcDateTimeFromLocalDepartement(
    endOfDay(new Date(parseInt(year), parseInt(month) - 1, parseInt(day))),
    departementCode
  )
  return toISOStringWithoutMilliseconds(endOfBookingLimitDayUtcDatetime)
}

export const buildDateTime = (date: string, time: string) => {
  const hoursAndMinutes = time.split(':')
  if (!isDateValid(date) || hoursAndMinutes.length < 2) {
    throw Error('La date ou l’heure est invalide')
  }
  const [hours, minutes] = hoursAndMinutes
  const [year, month, day] = date.split('-')

  // new Date(year, month, day, hours, minutes)
  return new Date(
    parseInt(year),
    parseInt(month) - 1,
    parseInt(day),
    parseInt(hours),
    parseInt(minutes)
  )
}

export const serializeDateTimeToUTCFromLocalDepartment = (
  beginningDate: string,
  beginningTime: string,
  departementCode?: string | null
): string => {
  const beginningDateTimeInUserTimezone = buildDateTime(
    beginningDate,
    beginningTime
  )

  const beginningDateTimeInUTCTimezone = getUtcDateTimeFromLocalDepartement(
    beginningDateTimeInUserTimezone,
    departementCode
  )

  return toISOStringWithoutMilliseconds(beginningDateTimeInUTCTimezone)
}

const serializeStockEvent = (
  formValues: StockEventFormValues,
  departementCode?: string | null
): EventStockUpdateBodyModel => {
  if (!isDateValid(formValues.beginningDate)) {
    throw Error("La date de début d'évenement est invalide")
  }
  if (formValues.beginningTime === '') {
    throw Error("L'heure de début d'évenement est invalide")
  }
  if (formValues.priceCategoryId === '') {
    throw Error('Le tarif est invalide')
  }

  const serializedbeginningDatetime = serializeDateTimeToUTCFromLocalDepartment(
    formValues.beginningDate,
    formValues.beginningTime,
    departementCode
  )

  return {
    id: formValues.stockId,
    beginningDatetime: serializedbeginningDatetime,
    bookingLimitDatetime: isDateValid(formValues.bookingLimitDatetime)
      ? serializeBookingLimitDatetime(
          formValues.beginningDate,
          formValues.beginningTime,
          formValues.bookingLimitDatetime,
          departementCode
        )
      : serializedbeginningDatetime,
    priceCategoryId: parseInt(formValues.priceCategoryId),
    quantity: formValues.remainingQuantity
      ? formValues.remainingQuantity + formValues.bookingsQuantity
      : null,
  }
}

export const serializeStockEventEdition = (
  formValuesList: StockEventFormValues[],
  departementCode?: string | null
): EventStockUpdateBodyModel[] => {
  const today = getToday()
  return formValuesList
    .filter((stockFormValues) => {
      const beginningDatetime =
        stockFormValues.beginningDate !== '' &&
        stockFormValues.beginningTime !== ''
          ? buildDateTime(
              stockFormValues.beginningDate,
              stockFormValues.beginningTime
            )
          : null
      return beginningDatetime === null || beginningDatetime >= today
    })
    .map((formValues: StockEventFormValues) =>
      serializeStockEvent(formValues, departementCode)
    )
}
