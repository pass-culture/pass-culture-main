import type {
  ThingStocksBulkUpsertBodyModel,
  ThingStockUpsertBodyModel,
} from '@/apiClient/v1'
import { isDateValid } from '@/commons/utils/date'
import type { Defined } from '@/commons/utils/types'

import type {
  PriceTableEntryFormValues,
  PriceTableFormValues,
} from '../schemas'
import { toBookingLimitDatetime } from './toBookingLimitDatetime'

// We use `Defined` because it seems there is no way to generate non-omittable but nullable fields with Spectree
const toThingStockUpsertBodyModel = (
  entry: PriceTableEntryFormValues,
  {
    departementCode,
  }: {
    departementCode?: string | null
  }
): Defined<ThingStockUpsertBodyModel> => {
  const activationCodesExpirationDatetime: string | null =
    (entry.activationCodes ?? []).length > 0 &&
    isDateValid(entry.activationCodesExpirationDatetime)
      ? toBookingLimitDatetime(departementCode)
      : null
  const bookingLimitDatetime = isDateValid(entry.bookingLimitDatetime)
    ? toBookingLimitDatetime(entry.bookingLimitDatetime, departementCode)
    : null
  const price = entry.price ? entry.price : 0
  const quantity = entry.quantity ?? null

  const stock: Defined<ThingStockUpsertBodyModel> = {
    id: entry.id,
    activationCodes: entry.activationCodes,
    activationCodesExpirationDatetime,
    bookingLimitDatetime,
    offerId: entry.offerId,
    price,
    quantity,
  }

  const activationCodes = (entry.activationCodes ?? []) as string[]
  if (activationCodes.length > 0) {
    stock.activationCodes = activationCodes
    if (isDateValid(entry.activationCodesExpirationDatetime)) {
      stock.activationCodesExpirationDatetime = toBookingLimitDatetime(
        entry.activationCodesExpirationDatetime,
        departementCode
      )
    }
  }

  return stock
}

export const toThingStocksBulkUpsertBodyModel = (
  formValues: PriceTableFormValues,
  {
    departementCode,
  }: {
    departementCode?: string | null
  }
): ThingStocksBulkUpsertBodyModel => {
  const stocks = formValues.entries.map((entry) =>
    toThingStockUpsertBodyModel(entry, { departementCode })
  )

  return { stocks }
}
