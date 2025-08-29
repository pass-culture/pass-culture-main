import type { GetIndividualOfferWithAddressResponseModel } from '@/apiClient/v1'
import { OFFER_WIZARD_MODE } from '@/commons/core/Offers/constants'
import { getToday, getYearMonthDay, isDateValid } from '@/commons/utils/date'
import { getDepartmentCode } from '@/commons/utils/getDepartmentCode'
import { getLocalDepartementDateTimeFromUtc } from '@/commons/utils/timezone'

import type { PriceTableEntryFormValues } from '../schemas'

const getBookingLimitDateMax = (date: Date | undefined) => {
  if (date === undefined) {
    return undefined
  }

  const result = new Date(date)
  result.setDate(result.getDate() - 7)

  return result
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
    const [
      bookingLimitDatetimeYear,
      bookingLimitDatetimeMonth,
      bookingLimitDatetimeDay,
    ] = getYearMonthDay(entry.bookingLimitDatetime ?? '')
    const [
      activationCodesExpirationDatetimeYear,
      activationCodesExpirationDatetimeMonth,
      activationCodesExpirationDatetimeDay,
    ] = getYearMonthDay(entry.activationCodesExpirationDatetime ?? '')

    const activationCodesExpirationDatetimeMin = isDateValid(
      entry.bookingLimitDatetime
    )
      ? new Date(
          bookingLimitDatetimeYear,
          bookingLimitDatetimeMonth,
          bookingLimitDatetimeDay
        )
      : null

    const activationCodesExpirationDatetimeAsDate: Date | undefined =
      isDateValid(entry.activationCodesExpirationDatetime)
        ? new Date(
            activationCodesExpirationDatetimeYear,
            activationCodesExpirationDatetimeMonth,
            activationCodesExpirationDatetimeDay
          )
        : undefined

    const bookingLimitDatetimeMax = getBookingLimitDateMax(
      activationCodesExpirationDatetimeAsDate
    )

    const quantityMin =
      mode === OFFER_WIZARD_MODE.EDITION ? (entry.bookingsQuantity ?? 0) : 1

    return {
      activationCodesExpirationDatetimeMin,
      bookingLimitDatetimeMin: nowAsDate,
      bookingLimitDatetimeMax,
      nowAsDate,
      quantityMin,
    }
  }

  return {
    computeEntryConstraints,
    nowAsDate,
  }
}
