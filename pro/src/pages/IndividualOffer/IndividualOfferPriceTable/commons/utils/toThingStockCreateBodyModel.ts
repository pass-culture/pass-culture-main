import type { ThingStockCreateBodyModel } from '@/apiClient/v1'
import { isDateValid } from '@/commons/utils/date'

import type { PriceTableFormValues } from '../schemas'
import { toBookingLimitDatetime } from './toBookingLimitDatetime'

export const toThingStockCreateBodyModel = (
  formValues: PriceTableFormValues,
  {
    departementCode,
  }: {
    departementCode?: string | null
  }
): ThingStockCreateBodyModel => {
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

  const apiStock: ThingStockCreateBodyModel = {
    bookingLimitDatetime,
    price,
    quantity,
    offerId: firstEntry.offerId,
  }

  const activationCodes = (firstEntry.activationCodes ?? []) as string[]
  if (activationCodes.length > 0) {
    apiStock.activationCodes = activationCodes
    const expiration = firstEntry.activationCodesExpirationDatetime as
      | string
      | Date
      | null
      | undefined
    if (isDateValid(expiration)) {
      apiStock.activationCodesExpirationDatetime = toBookingLimitDatetime(
        expiration,
        departementCode
      )
    }
  }

  return apiStock
}
