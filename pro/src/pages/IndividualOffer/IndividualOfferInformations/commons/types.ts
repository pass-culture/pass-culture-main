import { WithdrawalTypeEnum } from 'apiClient/v1'
import { AccessibilityFormValues } from 'commons/core/shared/types'

export type UsefulInformationFormValues = {
  isEvent?: boolean
  isNational: boolean
  withdrawalDelay?: number | null
  withdrawalType?: WithdrawalTypeEnum | null
  withdrawalDetails?: string
  accessibility: AccessibilityFormValues
  receiveNotificationEmails: boolean
  bookingEmail: string
  externalTicketOfficeUrl?: string | null
  bookingContact?: string
  offerLocation?: string | undefined
  manuallySetAddress?: boolean
  'search-addressAutocomplete'?: string
  addressAutocomplete?: string
  coords?: string
  banId?: string | null
  inseeCode?: string | null
  locationLabel?: string | null
  street?: string | null
  postalCode?: string
  city?: string
  latitude?: string
  longitude?: string
}
