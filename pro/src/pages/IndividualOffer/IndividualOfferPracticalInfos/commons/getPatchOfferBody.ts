import { WithdrawalTypeEnum } from '@/apiClient/v1'
import { serializeDateTimeToUTCFromLocalDepartment } from '@/commons/utils/timezone'

import type { IndividualOfferPracticalInfosFormValues } from './types'

export function getPatchOfferBody(
  formValues: IndividualOfferPracticalInfosFormValues,
  departmentCode: string,
  shouldSendMail: boolean
) {
  const withdrawalDelayNullishValue =
    formValues.withdrawalType === WithdrawalTypeEnum.NO_TICKET
      ? null
      : undefined
  const withdrawalDelay =
    formValues.withdrawalDelay === undefined
      ? withdrawalDelayNullishValue
      : Number(formValues.withdrawalDelay)

  const formattedBookabilityDate =
    formValues.bookingAllowedDate && formValues.bookingAllowedTime
      ? serializeDateTimeToUTCFromLocalDepartment(
          formValues.bookingAllowedDate,
          formValues.bookingAllowedTime,
          departmentCode
        )
      : undefined

  return {
    bookingContact: formValues.bookingContact,
    bookingEmail: !formValues.receiveNotificationEmails
      ? null
      : formValues.bookingEmail,
    externalTicketOfficeUrl: !formValues.externalTicketOfficeUrl
      ? null
      : formValues.externalTicketOfficeUrl,
    shouldSendMail: shouldSendMail,
    withdrawalDelay,
    withdrawalDetails: formValues.withdrawalDetails ?? undefined,
    withdrawalType: formValues.withdrawalType,
    bookingAllowedDatetime:
      formValues.bookingAllowedMode === 'later'
        ? formattedBookabilityDate
        : null,
  }
}
