import { WithdrawalTypeEnum } from 'apiClient/v1'
import { AccessibilityFormValues } from 'commons/core/shared/types'

// TODO (igabriele, 2025-07-24): Make this type stricter (regarding optionals & null vs undefined).
export type UsefulInformationFormValues = {
  accessibility?: AccessibilityFormValues
  addressAutocomplete?: string
  banId?: string
  bookingContact?: string
  bookingEmail?: string
  city?: string
  coords?: string
  externalTicketOfficeUrl?: string
  inseeCode?: string
  isEvent?: boolean
  isNational?: boolean
  latitude?: string
  locationLabel?: string
  longitude?: string
  manuallySetAddress?: boolean
  offerLocation?: string
  postalCode?: string
  receiveNotificationEmails?: boolean
  'search-addressAutocomplete'?: string
  street?: string
  url?: string
  withdrawalDelay?: string
  withdrawalType?: WithdrawalTypeEnum
  withdrawalDetails?: string
}
