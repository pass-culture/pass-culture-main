import type { GetIndividualOfferResponseModelV2 } from '@/apiClient/v1'
import {
  type SubcategoryResponseModel,
  WithdrawalTypeEnum,
} from '@/apiClient/v1'

import type { IndividualOfferPracticalInfosFormValues } from './types'

export function getInitialValuesFromOffer(
  offer: GetIndividualOfferResponseModelV2,
  offerSubcategory?: SubcategoryResponseModel
): IndividualOfferPracticalInfosFormValues {
  return {
    withdrawalDetails: offer.withdrawalDetails ?? null,
    withdrawalDelay: offer.withdrawalDelay?.toString() ?? null,
    withdrawalType:
      offer.withdrawalType ??
      (offerSubcategory?.canBeWithdrawable
        ? WithdrawalTypeEnum.NO_TICKET
        : null),
    bookingEmail: offer.bookingEmail ?? null,
    bookingContact: offer.bookingContact ?? null,
    receiveNotificationEmails: Boolean(offer.bookingEmail),
    externalTicketOfficeUrl: offer.externalTicketOfficeUrl ?? null,
  }
}
