import { format } from 'date-fns'
import sub from 'date-fns/sub'

import { StocksEvent } from 'components/StocksEventList/StocksEventList'
import useNotification from 'hooks/useNotification'
import { MAX_STOCKS_PER_OFFER } from 'screens/IndividualOffer/constants'
import { serializeBeginningDateTime } from 'screens/IndividualOffer/StocksEventEdition/adapters/serializers'
import upsertStocksEventAdapter from 'screens/IndividualOffer/StocksEventEdition/adapters/upsertStocksEventAdapter'
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

export const onSubmit = async (
  values: RecurrenceFormValues,
  departmentCode: string,
  existingStocks: StocksEvent[],
  offerId: number,
  notify: ReturnType<typeof useNotification>
): Promise<StocksEvent[] | undefined | void> => {
  const dates = getRecurrenceDates(values)
  const generatedStocks = generateStocksForDates(values, dates, departmentCode)

  if (generatedStocks.length + existingStocks.length > MAX_STOCKS_PER_OFFER) {
    notify.error(
      `Veuillez créer moins de ${MAX_STOCKS_PER_OFFER} occurrences par offre.`
    )
    return
  }

  const allStocks: StocksEvent[] = [...existingStocks, ...generatedStocks]

  const uniqueStocksSet = new Set()

  const deduplicatedStocks: StocksEvent[] = allStocks.filter((stock) => {
    const stockKey = `${stock.beginningDatetime}-${stock.priceCategoryId}`
    if (!uniqueStocksSet.has(stockKey)) {
      uniqueStocksSet.add(stockKey)
      return true
    }
    return false
  })

  const serializedStocksToAdd = deduplicatedStocks
    //  keep only the new stocks
    .filter((s) => s.id === undefined)
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
  const numberOfRemovedStocks = allStocks.length - deduplicatedStocks.length

  if (numberOfRemovedStocks > 0) {
    // FIXED in same PR this notification is never shown
    notify.information(
      numberOfRemovedStocks === 1
        ? 'Une occurence n’a pas été ajoutée car elle existait déjà'
        : 'Certaines occurences n’ont pas été ajoutées car elles existaient déjà'
    )
  }

  // Upsert stocks if there are stocks to upsert
  if (serializedStocksToAdd.length > 0) {
    const { isOk } = await upsertStocksEventAdapter({
      offerId: offerId,
      stocks: serializedStocksToAdd,
    })
    if (isOk) {
      notify.success(
        serializedStocksToAdd.length === 1
          ? '1 nouvelle occurrence a été ajoutée'
          : `${serializedStocksToAdd.length} nouvelles occurrences ont été ajoutées`
      )
    } else {
      notify.error(
        "Une erreur est survenue lors de l'enregistrement de vos stocks."
      )
      return
    }
  }

  // FIXED in same PR this break deletion because we need ids now
  return deduplicatedStocks
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
  departmentCode?: string | null
): StocksEvent[] =>
  dates.flatMap((beginningDate) =>
    values.beginningTimes.flatMap((beginningTime) =>
      values.quantityPerPriceCategories.flatMap((quantityPerPriceCategory) => {
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
          bookingsQuantity: 0,
          isEventDeletable: true,
        }
      })
    )
  )
