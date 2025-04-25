import {
  addDays,
  format,
  getISODay,
  isAfter,
  isBefore,
  isSameDay,
  sub,
} from 'date-fns'

import {
  FORMAT_ISO_DATE_ONLY,
  toISOStringWithoutMilliseconds,
} from 'commons/utils/date'
import { serializeDateTimeToUTCFromLocalDepartment } from 'components/IndividualOffer/StocksEventEdition/serializers'
import { StocksEvent } from 'components/StocksEventList/StocksEventList'

import { weekDays } from '../form/constants'
import { StocksCalendarFormValues } from '../form/types'

export class GetStocksCustomError extends Error {
  public customMessage: string = ''
  public stockTimeSlotIndexes: number[] = []
  constructor(m: string, indexes?: number[]) {
    super()
    this.customMessage = m
    this.stockTimeSlotIndexes = indexes || []
  }
}

export function getStocksForMultipleDays(
  formValues: StocksCalendarFormValues,
  departmentCode: string
): Partial<StocksEvent>[] {
  const startDate = formValues.multipleDaysStartDate
  const endDate = formValues.multipleDaysEndDate

  if (!startDate || !endDate) {
    throw new Error('Selected dates are invalid')
  }

  const checkedWeekDays = formValues.multipleDaysWeekDays
    .filter((wd) => wd.checked)
    .map((wd) => wd.value)

  return getDayDatesInBetweenDates(new Date(startDate), new Date(endDate))
    .filter((d) =>
      //  Only keep the days of the week that are checked
      checkedWeekDays.includes(weekDays[getISODay(d) - 1].value)
    )
    .flatMap((d) => getStocksForOneDay(d, formValues, departmentCode))
}

export function getStocksForOneDay(
  date: Date,
  formValues: StocksCalendarFormValues,
  departmentCode: string
): Partial<StocksEvent>[] {
  const times = formValues.specificTimeSlots.map((s) => s.slot)

  if (times.length === 0) {
    throw new GetStocksCustomError('Les horaires sélectionnés sont invalides.')
  }

  const formattedDate = format(date, FORMAT_ISO_DATE_ONLY)

  const serializedTimes = times.map((t) =>
    serializeDateTimeToUTCFromLocalDepartment(formattedDate, t, departmentCode)
  )

  const invalidTimesIndexes = serializedTimes
    .map((dateTime, i) => (isBefore(new Date(), dateTime) ? null : i))
    .filter((index) => index !== null)

  if (invalidTimesIndexes.length > 0) {
    throw new GetStocksCustomError(
      "Vous ne pouvez pas ajouter d'horaires dans le passé",
      invalidTimesIndexes
    )
  }

  return serializedTimes.flatMap((dateTime) => {
    return formValues.pricingCategoriesQuantities.map(
      (quantityPerPriceCategory) => {
        const quantity = quantityPerPriceCategory.quantity || null

        return {
          priceCategoryId: parseInt(quantityPerPriceCategory.priceCategory),
          quantity: quantity !== null ? Number(quantity) : quantity,
          beginningDatetime: dateTime,
          bookingLimitDatetime: toISOStringWithoutMilliseconds(
            sub(new Date(dateTime), {
              days: Number(formValues.bookingLimitDateInterval || 0),
            })
          ),
        }
      }
    )
  })
}

export function getWeekDaysInBetweenDates(
  date1: Date,
  date2: Date
): typeof weekDays {
  const recurrencedays = []

  let date = date1
  while (isAfter(date2, date) || isSameDay(date2, date)) {
    recurrencedays.push(weekDays[getISODay(date) - 1])
    date = addDays(date, 1)
  }

  return recurrencedays
}

function getDayDatesInBetweenDates(date1: Date, date2: Date): Date[] {
  const dates = []

  let date = date1
  while (isAfter(date2, date) || isSameDay(date2, date)) {
    dates.push(date)
    date = addDays(date, 1)
  }

  return dates
}
