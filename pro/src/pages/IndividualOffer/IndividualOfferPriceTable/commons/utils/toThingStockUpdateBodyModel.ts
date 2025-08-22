import type { ThingStockUpdateBodyModel } from '@/apiClient/v1'
import { isDateValid } from '@/commons/utils/date'

import type { PriceTableFormValues } from '../schemas'
import { toBookingLimitDatetime } from './toBookingLimitDatetime'

export const toThingStockUpdateBodyModel = (
  formValues: PriceTableFormValues,
  {
    departementCode,
  }: {
    departementCode?: string | null
  }
): ThingStockUpdateBodyModel => {
  const firstEntry = formValues.entries[0]

  const bookingLimitDate = firstEntry.bookingLimitDatetime as
    | string
    | Date
    | null
    | undefined
  const bookingLimitDatetime = isDateValid(bookingLimitDate)
    ? toBookingLimitDatetime(bookingLimitDate, departementCode)
    : null

  const price = firstEntry.price ? firstEntry.price : 0
  const quantity = firstEntry.quantity ?? null

  return { bookingLimitDatetime, price, quantity }
}
