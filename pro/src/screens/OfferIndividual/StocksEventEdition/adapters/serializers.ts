import endOfDay from 'date-fns/endOfDay'

import { StockCreationBodyModel, StockEditionBodyModel } from 'apiClient/v1'
import { StockEventFormValues } from 'screens/OfferIndividual/StocksEventEdition/StockFormList'
import {
  getToday,
  isDateValid,
  toISOStringWithoutMilliseconds,
} from 'utils/date'
import { getUtcDateTimeFromLocalDepartement } from 'utils/timezone'

const serializeBookingLimitDatetime = (
  beginningDate: string,
  beginningTime: string,
  bookingLimitDatetime: string,
  departementCode: string
) => {
  // If the bookingLimitDatetime is the same day as the start of the event
  // the bookingLimitDatetime should be set to beginningDate and beginningTime
  // ie : bookable until the event
  if (
    new Date(beginningDate).toDateString() ===
    new Date(bookingLimitDatetime).toDateString()
  ) {
    return serializeBeginningDateTime(
      beginningDate,
      beginningTime,
      departementCode
    )
  }
  const endOfBookingLimitDayUtcDatetime = getUtcDateTimeFromLocalDepartement(
    endOfDay(new Date(bookingLimitDatetime)),
    departementCode
  )
  return toISOStringWithoutMilliseconds(endOfBookingLimitDayUtcDatetime)
}

export const buildDateTime = (date: string, time: string) => {
  const [hours, minutes] = time.split(':')
  if (!isDateValid(date) || hours === undefined || minutes === undefined) {
    throw Error('La date ou l’heure est invalide')
  }
  const [year, month, day] = date.split('-')

  // previously method with :
  // set(new Date(date), {
  //   hours: parseInt(hours),
  //   minutes: parseInt(minutes),
  // })
  // introduced a bug on western timezone,
  // indeed new Date(date) return a date at 00h00 from user local timezone
  // once set it was the day before

  // new Date(year, month, day, hours, minutes)
  return new Date(
    parseInt(year),
    parseInt(month) - 1,
    parseInt(day),
    parseInt(hours),
    parseInt(minutes)
  )
}

export const serializeBeginningDateTime = (
  beginningDate: string,
  beginningTime: string,
  departementCode: string
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
  departementCode: string
): StockCreationBodyModel | StockEditionBodyModel => {
  if (!isDateValid(formValues.beginningDate)) {
    throw Error("La date de début d'évenement est invalide")
  }
  if (formValues.beginningTime === '') {
    throw Error("L'heure de début d'évenement est invalide")
  }

  const serializedbeginningDatetime = serializeBeginningDateTime(
    formValues.beginningDate,
    formValues.beginningTime,
    departementCode
  )
  const apiStock: StockCreationBodyModel = {
    beginningDatetime: serializedbeginningDatetime,
    bookingLimitDatetime: isDateValid(formValues.bookingLimitDatetime)
      ? serializeBookingLimitDatetime(
          formValues.beginningDate,
          formValues.beginningTime,
          formValues.bookingLimitDatetime,
          departementCode
        )
      : serializedbeginningDatetime,
    priceCategoryId:
      formValues.priceCategoryId !== ''
        ? parseInt(formValues.priceCategoryId)
        : null,
    quantity:
      formValues.remainingQuantity === ''
        ? null
        : formValues.remainingQuantity + formValues.bookingsQuantity,
  }
  if (formValues.stockId) {
    return {
      ...apiStock,
      id: formValues.stockId,
    }
  }
  return apiStock
}

export const serializeStockEventEdition = (
  formValuesList: StockEventFormValues[],
  departementCode: string
): StockCreationBodyModel[] | StockEditionBodyModel[] => {
  const today = getToday()
  return formValuesList
    .filter(stockFormValues => {
      const beginingDatetime =
        stockFormValues.beginningDate !== '' &&
        stockFormValues.beginningTime !== ''
          ? buildDateTime(
              stockFormValues.beginningDate,
              stockFormValues.beginningTime
            )
          : null
      return beginingDatetime === null || beginingDatetime >= today
    })
    .map((formValues: StockEventFormValues) =>
      serializeStockEvent(formValues, departementCode)
    )
}
