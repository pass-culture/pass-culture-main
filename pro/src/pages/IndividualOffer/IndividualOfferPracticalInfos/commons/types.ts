import type { WithdrawalTypeEnum } from '@/apiClient/v1'

export type IndividualOfferPracticalInfosFormValues = {
  bookingAllowedMode: 'now' | 'later'
  bookingAllowedDate?: string
  bookingAllowedTime?: string
  withdrawalType?: WithdrawalTypeEnum
  withdrawalDelay?: string
  withdrawalDetails?: string
  bookingContact?: string
  externalTicketOfficeUrl?: string
  receiveNotificationEmails?: boolean
  bookingEmail?: string
}
