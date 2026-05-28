import type {
  AccessibilityFormValues,
  FlatAddressFormValues,
} from '@/commons/core/shared/types'
import type { ActivityNotOpenToPublicType } from '@/commons/mappings/ActivityNotOpenToPublic'
import type { ActivityOpenToPublicType } from '@/commons/mappings/ActivityOpenToPublic'
import type { Nullable } from '@/commons/utils/types'

export type VenueSettingsFormContext = {
  isCaledonian: boolean
  siren: string | null
  withSiret: boolean
  isOpenToPublic?: string
  activity?: ActivityOpenToPublicType | ActivityNotOpenToPublicType | null
}

export interface VenueSettingsFormValues extends FlatAddressFormValues {
  comment: string
  name: string
  publicName: string
  siret: string
  venueSiret: number | ''
  withdrawalDetails: string
  manuallySetAddress?: boolean
  bookingEmail?: string
  isOpenToPublic: string
  activity?: ActivityOpenToPublicType | ActivityNotOpenToPublicType | null
  culturalDomains?: string[]
  description?: string
  accessibility: Nullable<AccessibilityFormValues>
  isAccessibilityAppliedOnAllOffers: boolean
}
