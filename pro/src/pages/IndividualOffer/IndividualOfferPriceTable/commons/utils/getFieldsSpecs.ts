import type { GetIndividualOfferWithAddressResponseModel } from '@/apiClient/v1'
import { OFFER_WIZARD_MODE } from '@/commons/core/Offers/constants'
import { assertOrFrontendError } from '@/commons/errors/assertOrFrontendError'
import { getToday, getYearMonthDay, isDateValid } from '@/commons/utils/date'
import { getDepartmentCode } from '@/commons/utils/getDepartmentCode'
import { getLocalDepartementDateTimeFromUtc } from '@/commons/utils/timezone'

import type { PriceTableEntryFormValues } from '../schemas'

export const getFieldsSpecs = ({
  entries,
  offer,
  mode,
}: {
  entries: PriceTableEntryFormValues[]
  offer: GetIndividualOfferWithAddressResponseModel
  mode: OFFER_WIZARD_MODE
}) => {
  const firstEntry = entries.at(0)
  assertOrFrontendError(firstEntry, '`entries` is empty.')

  const [minExpirationYear, minExpirationMonth, minExpirationDay] =
    getYearMonthDay(entries[0]?.bookingLimitDatetime ?? '')
  const minExpirationDate = isDateValid(entries[0]?.bookingLimitDatetime)
    ? new Date(minExpirationYear, minExpirationMonth, minExpirationDay)
    : null

  const minQuantity =
    mode === OFFER_WIZARD_MODE.EDITION ? (firstEntry.bookingsQuantity ?? 0) : 1

  const nowAsDate = getLocalDepartementDateTimeFromUtc(
    getToday(),
    getDepartmentCode(offer)
  )

  return {
    minExpirationDate,
    minQuantity,
    nowAsDate,
  }
}
