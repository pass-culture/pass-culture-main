import type { GetIndividualOfferWithAddressResponseModel } from '@/apiClient/v1'
import { OFFER_WIZARD_MODE } from '@/commons/core/Offers/constants'
import { getToday, getYearMonthDay, isDateValid } from '@/commons/utils/date'
import { getDepartmentCode } from '@/commons/utils/getDepartmentCode'
import { getLocalDepartementDateTimeFromUtc } from '@/commons/utils/timezone'

import type { PriceTableEntryFormValues } from '../schemas'

const getBookingLimitDateMax = (date: Date | null) => {
  if (!date) {
    return undefined
  }

  const result = new Date(date)
  result.setDate(result.getDate() - 7)

  return result
}

const toDateIfValid = (value: string | null) => {
  if (!isDateValid(value)) {
    return null
  }

  const [y, m, d] = getYearMonthDay(value)

  return new Date(y, m, d)
}

export const makeFieldConstraints = ({
  offer,
  mode,
}: {
  offer: GetIndividualOfferWithAddressResponseModel
  mode: OFFER_WIZARD_MODE
}) => {
  const nowAsDate = getLocalDepartementDateTimeFromUtc(
    getToday(),
    getDepartmentCode(offer)
  )

  const computeEntryConstraints = (entry: PriceTableEntryFormValues) => {
    const activationCodesExpirationDate = toDateIfValid(
      entry.activationCodesExpirationDatetime
    )

    return {
      activationCodesExpirationDatetimeMin: toDateIfValid(
        entry.bookingLimitDatetime
      ),
      bookingLimitDatetimeMin: nowAsDate,
      bookingLimitDatetimeMax: getBookingLimitDateMax(
        activationCodesExpirationDate
      ),
      nowAsDate,
      quantityMin:
        mode === OFFER_WIZARD_MODE.EDITION ? (entry.bookingsQuantity ?? 0) : 1,
    }
  }

  return {
    computeEntryConstraints,
    nowAsDate,
  }
}
