import type { FormikProps } from 'formik'

import { WithdrawalTypeEnum } from 'apiClient/v1'
import { AccessibilityFormValues } from 'core/shared/types'

export interface IndividualOfferFormValues {
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
  offerlocation?: string
  locationLabel?: string
  manuallySetAddress?: boolean
  'search-addressAutocomplete'?: string
  addressAutocomplete?: string
  street?: string
  postalCode?: string
  city?: string
  coords?: string
  latitude?: string
  longitude?: string
  banId?: string
}

export type IndividualOfferForm = FormikProps<IndividualOfferFormValues>
