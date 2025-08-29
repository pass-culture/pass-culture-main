import { format, isAfter } from 'date-fns'

import {
  type GetIndividualOfferWithAddressResponseModel,
  type SubcategoryResponseModel,
  WithdrawalTypeEnum,
} from '@/apiClient/v1'
import { FORMAT_HH_mm, formatShortDateForInput } from '@/commons/utils/date'
import { getLocalDepartementDateTimeFromUtc } from '@/commons/utils/timezone'

import type { IndividualOfferPracticalInfosFormValues } from './types'

export function getInitialValuesFromOffer(
  offer: GetIndividualOfferWithAddressResponseModel,
  offerSubcategory?: SubcategoryResponseModel
): IndividualOfferPracticalInfosFormValues {
  return {
    bookingAllowedMode:
      offer.bookingAllowedDatetime &&
      isAfter(offer.bookingAllowedDatetime, new Date())
        ? 'later'
        : 'now',
    bookingAllowedDate: offer.bookingAllowedDatetime
      ? formatShortDateForInput(
          getLocalDepartementDateTimeFromUtc(offer.bookingAllowedDatetime)
        )
      : undefined,
    bookingAllowedTime: offer.bookingAllowedDatetime
      ? format(
          getLocalDepartementDateTimeFromUtc(offer.bookingAllowedDatetime),
          FORMAT_HH_mm
        )
      : undefined,
    withdrawalDetails: offer.withdrawalDetails || '',
    withdrawalDelay:
      offer.withdrawalDelay === null
        ? undefined
        : offer.withdrawalDelay?.toString(),
    withdrawalType:
      offer.withdrawalType ||
      (offerSubcategory?.canBeWithdrawable
        ? WithdrawalTypeEnum.NO_TICKET
        : undefined),
    bookingEmail: offer.bookingEmail || '',
    bookingContact: offer.bookingContact || undefined,
    receiveNotificationEmails: Boolean(offer.bookingEmail),
    externalTicketOfficeUrl: offer.externalTicketOfficeUrl || '',
  }
}
