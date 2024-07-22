import { WithdrawalTypeEnum } from 'apiClient/v1'
import { AccessibilityFormValues } from 'core/shared/types'

export type UsefulInformationFormValues = {
  isEvent?: boolean
  isNational: boolean
  withdrawalDelay?: number | null
  withdrawalType?: WithdrawalTypeEnum | null
  withdrawalDetails?: string
  accessibility: AccessibilityFormValues
  receiveNotificationEmails: boolean
  bookingEmail: string
  externalTicketOfficeUrl: string
  url: string
  isVenueVirtual?: boolean
  bookingContact?: string
}
