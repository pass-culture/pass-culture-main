import { WithdrawalTypeEnum } from 'apiClient/v1'
import { AccessibilityFormValues } from 'commons/core/shared/types'
import { type AddressFormValues } from 'components/AddressManual/AddressManual' // We makes "AddressFormValues" partial because the individual offer form may not have address fields (e.g. if it's a virtual offer)

// We makes "AddressFormValues" partial because the individual offer form may not have address fields (e.g. if it's a virtual offer)
export interface IndividualOfferFormValues extends Partial<AddressFormValues> {
  isEvent?: boolean
  subCategoryFields: string[]
  name: string
  description: string
  offererId?: string
  venueId: string
  isNational: boolean
  categoryId: string
  subcategoryId: string
  showType: string
  showSubType: string
  withdrawalDetails: string
  musicType?: string
  musicSubType?: string
  gtl_id?: string
  withdrawalDelay?: number | null
  withdrawalType?: WithdrawalTypeEnum | null
  accessibility: AccessibilityFormValues
  author?: string
  performer?: string
  ean?: string
  speaker?: string
  stageDirector?: string
  visa?: string
  durationMinutes?: string | null
  receiveNotificationEmails: boolean
  bookingEmail: string
  isDuo: boolean
  url: string
  isVenueVirtual?: boolean
  bookingContact?: string
  offerLocation?: string | undefined
  locationLabel?: string | null
  manuallySetAddress?: boolean
}
