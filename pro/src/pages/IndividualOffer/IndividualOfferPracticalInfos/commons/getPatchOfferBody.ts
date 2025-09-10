import { WithdrawalTypeEnum } from '@/apiClient/v1'

import type { IndividualOfferPracticalInfosFormValues } from './types'

export function getPatchOfferBody(
  formValues: IndividualOfferPracticalInfosFormValues,
  shouldSendMail: boolean
) {
  const withdrawalDelayValue = formValues.withdrawalDelay
    ? Number(formValues.withdrawalDelay)
    : null

  const withdrawalDelayInBody =
    formValues.withdrawalType === WithdrawalTypeEnum.NO_TICKET
      ? null
      : withdrawalDelayValue

  return {
    bookingContact: formValues.bookingContact,
    bookingEmail: !formValues.receiveNotificationEmails
      ? null
      : formValues.bookingEmail,
    externalTicketOfficeUrl: !formValues.externalTicketOfficeUrl
      ? null
      : formValues.externalTicketOfficeUrl,
    shouldSendMail: shouldSendMail,
    withdrawalDelay: withdrawalDelayInBody,
    withdrawalDetails: formValues.withdrawalDetails ?? undefined,
    withdrawalType: formValues.withdrawalType,
  }
}
