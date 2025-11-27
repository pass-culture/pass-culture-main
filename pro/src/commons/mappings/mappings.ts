// Back-End Model Enums
import { DisplayedActivity } from '@/apiClient/v1/models/DisplayedActivity'
import { OnboardingActivity } from '@/apiClient/v1/models/OnboardingActivity'

// Client Mappings
import {
  _DisplayedActivityMappings,
  type DisplayedActivityType,
} from './DisplayedActivity'
import {
  _OnboardingActivityMappings,
  type OnboardingActivityType,
} from './OnboardingActivity'
import { buildFilteredMap } from './utils/buildFilteredMap'

// Getter for all activities that can be CHOSEN on the new structure registration
export const getActivities = (() => {
  const OnboardingActivityMap = buildFilteredMap(
    OnboardingActivity,
    _OnboardingActivityMappings
  )
  return (): Record<OnboardingActivityType, string> =>
    OnboardingActivityMap as Record<OnboardingActivityType, string>
})()

// Getter for all activities that can be DISPLAYED (including potential old ones)
export const getActivityLabel = (() => {
  const DisplayedActivityMap = buildFilteredMap(
    DisplayedActivity,
    _DisplayedActivityMappings
  )
  return (label: DisplayedActivityType): string => DisplayedActivityMap[label]
})()
