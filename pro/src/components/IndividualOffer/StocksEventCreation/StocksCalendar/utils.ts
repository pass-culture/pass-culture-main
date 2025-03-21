import { format, sub } from 'date-fns'

import {
  FORMAT_ISO_DATE_ONLY,
  toISOStringWithoutMilliseconds,
} from 'commons/utils/date'
import { serializeDateTimeToUTCFromLocalDepartment } from 'components/IndividualOffer/StocksEventEdition/serializers'
import { StocksEvent } from 'components/StocksEventList/StocksEventList'

import { StocksCalendarFormValues } from '../form/types'

export function getStocksForOneDay(
  formValues: StocksCalendarFormValues,
  departmentCode: string
): Partial<StocksEvent>[] {
  const date = formValues.oneDayDate
  const times = formValues.specificTimeSlots.map((s) => s.slot)

  if (!date || times.length === 0) {
    throw new Error('Selected date is invalid')
  }

  const formattedDate = format(date, FORMAT_ISO_DATE_ONLY)

  return times.flatMap((t) => {
    const dateTime = serializeDateTimeToUTCFromLocalDepartment(
      formattedDate,
      t,
      departmentCode
    )

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
