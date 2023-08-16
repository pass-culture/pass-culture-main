import { format } from 'date-fns'
import sub from 'date-fns/sub'
import { v4 as uuidv4 } from 'uuid'

import { StocksEvent } from 'components/StocksEventList/StocksEventList'
import { serializeBeginningDateTime } from 'screens/OfferIndividual/StocksEventEdition/adapters/serializers'
import {
  FORMAT_ISO_DATE_ONLY,
  isDateValid,
  toISOStringWithoutMilliseconds,
} from 'utils/date'

import {
  getDatesInInterval,
  getDatesWithMonthlyOption,
} from './recurrenceUtils'
import { RecurrenceFormValues, RecurrenceType } from './types'

export const onSubmit = (
  values: RecurrenceFormValues,
  departmentCode: string
): StocksEvent[] => {
  const dates = getRecurrenceDates(values)
  return generateStocksForDates(values, dates, departmentCode)
}

const getYearMonthDay = (date: string) => {
  const [year, month, day] = date.split('-')
  return {
    year: parseInt(year),
    month: parseInt(month) - 1,
    day: parseInt(day),
  }
}

const getRecurrenceDates = (values: RecurrenceFormValues): Date[] => {
  switch (values.recurrenceType) {
    case RecurrenceType.UNIQUE: {
      /* istanbul ignore next: should be already validated by yup */
      if (!isDateValid(values.startingDate)) {
        throw new Error('Starting date is empty')
      }
      const { year, month, day } = getYearMonthDay(values.startingDate)
      return [new Date(year, month, day)]
    }

    case RecurrenceType.DAILY: {
      /* istanbul ignore next: should be already validated by yup */
      if (
        !isDateValid(values.startingDate) ||
        !isDateValid(values.endingDate)
      ) {
        throw new Error('Starting or ending date is empty')
      }
      const {
        year: startYear,
        month: startMonth,
        day: startDay,
      } = getYearMonthDay(values.startingDate)
      const {
        year: endYear,
        month: endMonth,
        day: endDay,
      } = getYearMonthDay(values.endingDate)

      return getDatesInInterval(
        new Date(startYear, startMonth, startDay),
        new Date(endYear, endMonth, endDay)
      )
    }

    case RecurrenceType.WEEKLY: {
      /* istanbul ignore next: should be already validated by yup */
      if (
        !isDateValid(values.startingDate) ||
        !isDateValid(values.endingDate) ||
        values.days.length === 0
      ) {
        throw new Error('Starting, ending date or days is empty')
      }
      const {
        year: startYear,
        month: startMonth,
        day: startDay,
      } = getYearMonthDay(values.startingDate)
      const {
        year: endYear,
        month: endMonth,
        day: endDay,
      } = getYearMonthDay(values.endingDate)

      return getDatesInInterval(
        new Date(startYear, startMonth, startDay),
        new Date(endYear, endMonth, endDay),
        values.days
      )
    }
    case RecurrenceType.MONTHLY: {
      /* istanbul ignore next: should be already validated by yup */
      if (
        !isDateValid(values.startingDate) ||
        !isDateValid(values.endingDate)
      ) {
        throw new Error('Starting or ending date is empty')
      }
      if (values.monthlyOption === null) {
        throw new Error('Monthly option is empty')
      }
      const {
        year: startYear,
        month: startMonth,
        day: startDay,
      } = getYearMonthDay(values.startingDate)
      const {
        year: endYear,
        month: endMonth,
        day: endDay,
      } = getYearMonthDay(values.endingDate)

      return getDatesWithMonthlyOption(
        new Date(startYear, startMonth, startDay),
        new Date(endYear, endMonth, endDay),
        values.monthlyOption
      )
    }

    default:
      /* istanbul ignore next: should be already validated by yup */
      throw new Error(`Unhandled recurrence type: ${values.recurrenceType}`)
  }
}

const generateStocksForDates = (
  values: RecurrenceFormValues,
  dates: Date[],
  departmentCode: string
): StocksEvent[] =>
  dates.flatMap(beginningDate =>
    values.beginningTimes.flatMap(beginningTime =>
      values.quantityPerPriceCategories.flatMap(quantityPerPriceCategory => {
        /* istanbul ignore next: should be already validated by yup */
        if (beginningTime === '') {
          throw new Error('Some values are empty')
        }

        const beginningDatetime = serializeBeginningDateTime(
          format(beginningDate, FORMAT_ISO_DATE_ONLY),
          beginningTime,
          departmentCode
        )
        const bookingLimitDateInterval =
          values.bookingLimitDateInterval === ''
            ? 0
            : values.bookingLimitDateInterval

        return {
          priceCategoryId: parseInt(quantityPerPriceCategory.priceCategory),
          quantity:
            quantityPerPriceCategory.quantity === ''
              ? null
              : quantityPerPriceCategory.quantity,
          beginningDatetime,
          bookingLimitDatetime: toISOStringWithoutMilliseconds(
            sub(new Date(beginningDatetime), {
              days: bookingLimitDateInterval,
            })
          ),
          uuid: uuidv4(),
        }
      })
    )
  )
