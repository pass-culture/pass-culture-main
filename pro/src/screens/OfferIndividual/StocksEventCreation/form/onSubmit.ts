import sub from 'date-fns/sub'

import { StocksEvent } from 'components/StocksEventList/StocksEventList'
import { serializeBeginningDateTime } from 'screens/OfferIndividual/StocksEventEdition/adapters/serializers'
import { toISOStringWithoutMilliseconds } from 'utils/date'

import { getDatesInInterval } from './recurrenceUtils'
import { RecurrenceFormValues, RecurrenceType } from './types'

export const onSubmit = (
  values: RecurrenceFormValues,
  departmentCode: string
): StocksEvent[] => {
  const dates = getRecurrenceDates(values)

  return generateStocksForDates(values, dates, departmentCode)
}

const getRecurrenceDates = (values: RecurrenceFormValues): Date[] => {
  switch (values.recurrenceType) {
    case RecurrenceType.UNIQUE:
      /* istanbul ignore next: should be already validated by yup */
      if (values.startingDate === null) {
        throw new Error('Starting date is empty')
      }
      return [new Date(values.startingDate)]

    case RecurrenceType.DAILY: {
      /* istanbul ignore next: should be already validated by yup */
      if (values.startingDate === null || values.endingDate === null) {
        throw new Error('Starting or ending date is empty')
      }

      return getDatesInInterval(values.startingDate, values.endingDate)
    }

    case RecurrenceType.WEEKLY: {
      /* istanbul ignore next: should be already validated by yup */
      if (
        values.startingDate === null ||
        values.endingDate === null ||
        values.days.length === 0
      ) {
        throw new Error('Starting, ending date or days is empty')
      }

      return getDatesInInterval(
        values.startingDate,
        values.endingDate,
        values.days
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
        if (beginningTime === null) {
          throw new Error('Some values are empty')
        }

        const beginningDatetime = serializeBeginningDateTime(
          beginningDate,
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
        }
      })
    )
  )
