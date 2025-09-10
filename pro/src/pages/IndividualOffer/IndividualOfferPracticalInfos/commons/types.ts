import type { WithdrawalTypeEnum } from '@/apiClient/v1'

export type IndividualOfferPracticalInfosFormValues = {
  withdrawalType: WithdrawalTypeEnum | null
  withdrawalDelay: string | null
  withdrawalDetails: string | null
  bookingContact: string | null
  externalTicketOfficeUrl: string | null
  receiveNotificationEmails: boolean
  bookingEmail: string | null
}
