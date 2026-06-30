import type {
  ActivityNotOpenToPublic,
  ActivityOpenToPublic,
} from '@/apiClient/v1'
import type {
  AccessibilityFormValues,
  FlatAddressFormValues,
} from '@/commons/core/shared/types'
import type { Nullable } from '@/commons/utils/types'

export type VenueSettingsFormContext = {
  isCaledonian: boolean
  siren: string | null
  withSiret: boolean
  siret?: string | null
  isOpenToPublic?: string
  activity?: ActivityOpenToPublic | ActivityNotOpenToPublic | null
}

export interface VenueSettingsFormValues extends FlatAddressFormValues {
  comment: string
  name: string
  publicName: string
  siret: string
  venueSiret: number | ''
  withdrawalDetails: string
  manuallySetAddress?: boolean
  isOpenToPublic: string
  activity?: ActivityOpenToPublic | ActivityNotOpenToPublic | null
  culturalDomains?: string[]
  description?: string
  accessibility: Nullable<AccessibilityFormValues>
  isAccessibilityAppliedOnAllOffers: boolean
}
