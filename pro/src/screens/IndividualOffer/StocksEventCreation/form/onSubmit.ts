import { format, sub } from 'date-fns'

import { api } from 'apiClient/api'
import { StocksEvent } from 'components/StocksEventList/StocksEventList'
import { useNotification } from 'hooks/useNotification'
import { serializeDateTimeToUTCFromLocalDepartment } from 'screens/IndividualOffer/StocksEventEdition/serializers'
import {
  FORMAT_ISO_DATE_ONLY,
  isDateValid,
  toISOStringWithoutMilliseconds,
} from 'utils/date'

import {
  getDatesInInterval,
  getDatesWithMonthlyOption,
  isTimeInTheFuture,
} from './recurrenceUtils'
import { RecurrenceFormValues, RecurrenceType } from './types'

type StocksEventWithOptionalId = Omit<StocksEvent, 'id'> & { id?: number }

export const onSubmit = async (
  values: RecurrenceFormValues,
  departmentCode: string,
  offerId: number,
  notify: ReturnType<typeof useNotification>
): Promise<StocksEvent[] | void> => {
  const dates = getRecurrenceDates(values)
  const generatedStocks = generateStocksForDates(values, dates, departmentCode)

  const serializedStocksToAdd = generatedStocks
    // keep only the fields that are needed for the API
    .map(
      ({
        id,
        beginningDatetime,
        bookingLimitDatetime,
        priceCategoryId,
        quantity,
      }) => ({
        id,
        beginningDatetime,
        bookingLimitDatetime,
        priceCategoryId,
        quantity,
      })
    )

  // Upsert stocks if there are stocks to upsert
  if (serializedStocksToAdd.length > 0) {
    try {
      const { stocks_count } = await api.upsertStocks({
        offerId,
        stocks: serializedStocksToAdd,
      })
      notify.success(
        stocks_count > 1
          ? `${new Intl.NumberFormat('fr-FR').format(
              stocks_count
            )} nouvelles dates ont été ajoutées`
          : `${stocks_count} nouvelle date a été ajoutée`
      )
    } catch {
      notify.error(
        'Une erreur est survenue lors de l’enregistrement de vos stocks.'
      )
    }
  }
}

const getYearMonthDay = (date: string) => {
  const [year, month, day] = date.split('-')
  return {
    year: parseInt(year ?? ''),
    month: parseInt(month ?? '') - 1,
    day: parseInt(day ?? ''),
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
  departmentCode?: string | null
): StocksEventWithOptionalId[] =>
  dates.flatMap((beginningDate) =>
    values.beginningTimes
      // We filter out the times that are in the past for today
      .filter((beginningTime) =>
        isTimeInTheFuture(beginningDate, beginningTime)
      )
      .flatMap((beginningTime) =>
        values.quantityPerPriceCategories.flatMap(
          (quantityPerPriceCategory) => {
            /* istanbul ignore next: should be already validated by yup */
            if (beginningTime === '') {
              throw new Error('Some values are empty')
            }

            const beginningDatetime = serializeDateTimeToUTCFromLocalDepartment(
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
              bookingsQuantity: 0,
              isEventDeletable: true,
            }
          }
        )
      )
  )
