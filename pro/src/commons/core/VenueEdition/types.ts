import type {
  ActivityNotOpenToPublic,
  ActivityOpenToPublic,
  WeekdayOpeningHoursTimespans,
} from '@/apiClient/v1'
import type { AccessibilityFormValues } from '@/commons/core/shared/types'
import type { Nullable } from '@/commons/utils/types'

export interface VenueEditionFormValues {
  accessibility: Nullable<AccessibilityFormValues>
  description?: string
  email?: string | null
  isAccessibilityAppliedOnAllOffers: boolean
  phoneNumber?: string | null
  webSite?: string | null
  isOpenToPublic: string
  openingHours?: WeekdayOpeningHoursTimespans | null
  activity?: ActivityOpenToPublic | ActivityNotOpenToPublic | null
  culturalDomains?: string[]
  volunteeringUrl?: string | null
  withdrawalDetails?: string | null
}
