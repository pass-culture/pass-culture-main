import type { WeekdayOpeningHoursTimespans } from '@/apiClient/v1'
import type { AccessibilityFormValues } from '@/commons/core/shared/types'
import type { ActivityOpenToPublicType } from '@/commons/mappings/ActivityOpenToPublic'

export interface VenueEditionFormValues {
  accessibility: AccessibilityFormValues
  description?: string
  email?: string | null
  isAccessibilityAppliedOnAllOffers: boolean
  phoneNumber?: string | null
  webSite?: string | null
  isOpenToPublic: string
  openingHours?: WeekdayOpeningHoursTimespans | null
  activity?: ActivityOpenToPublicType | null
}
