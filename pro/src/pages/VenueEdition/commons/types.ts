import type { WeekdayOpeningHoursTimespans } from '@/apiClient/v1'
import type { AccessibilityFormValues } from '@/commons/core/shared/types'
import type { OnboardingActivityType } from '@/commons/mappings/OnboardingActivity'

export interface VenueEditionFormValues {
  accessibility: Partial<AccessibilityFormValues>
  description?: string
  email?: string | null
  isAccessibilityAppliedOnAllOffers: boolean
  phoneNumber?: string | null
  webSite?: string | null
  isOpenToPublic: string
  openingHours?: WeekdayOpeningHoursTimespans | null
  activity?: OnboardingActivityType | null
  culturalDomains?: string[]
}
