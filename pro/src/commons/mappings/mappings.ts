// Back-End Model Enums
import { DisplayedActivity } from '@/apiClient/v1/models/DisplayedActivity'
import { OnboardingActivityOpenToPublic } from '@/apiClient/v1/models/OnboardingActivityOpenToPublic'

// Client Mappings
import {
  _DisplayedActivityMappings,
  type DisplayedActivityType,
} from './DisplayedActivity'
import {
  _OnboardingActivityOpenToPublicMappings,
  type OnboardingActivityOpenToPublicType,
} from './OnboardingActivityOpenToPublic'
import { buildFilteredMap } from './utils/buildFilteredMap'

// Getter for all activities that can be CHOSEN on the new structure registration
export const getActivities = (() => {
  const OnboardingActivityOpenToPublicMap = buildFilteredMap(
    OnboardingActivityOpenToPublic,
    _OnboardingActivityOpenToPublicMappings
  )
  return (): Record<OnboardingActivityOpenToPublicType, string> =>
    OnboardingActivityOpenToPublicMap as Record<
      OnboardingActivityOpenToPublicType,
      string
    >
})()

// Getter for all activities that can be DISPLAYED (including potential old ones)
export const getActivityLabel = (() => {
  const DisplayedActivityMap = buildFilteredMap(
    DisplayedActivity,
    _DisplayedActivityMappings
  )
  return (label: DisplayedActivityType): string => DisplayedActivityMap[label]
})()
