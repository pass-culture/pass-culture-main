import type { WeekdayOpeningHoursTimespans } from '@/apiClient/v1'
import type { AccessibilityFormValues } from '@/commons/core/shared/types'
import type { ActivityOpenToPublicType } from '@/commons/mappings/ActivityOpenToPublic'
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
  activity?: ActivityOpenToPublicType | null
  culturalDomains?: string[]
}
