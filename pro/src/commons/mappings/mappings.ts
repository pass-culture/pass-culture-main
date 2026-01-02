// Back-End Model Enums

import { ActivityOpenToPublic } from '@/apiClient/v1/models/ActivityOpenToPublic'
import { DisplayableActivity } from '@/apiClient/v1/models/DisplayableActivity'

import {
  _ActivityOpenToPublicMappings,
  type ActivityOpenToPublicType,
} from './ActivityOpenToPublic'
// Client Mappings
import {
  _DisplayableActivityMappings,
  type DisplayableActivityType,
} from './DisplayableActivity'
import { buildFilteredMap } from './utils/buildFilteredMap'

// Getter for all activities that can be CHOSEN on the new structure registration
export const getActivities = (() => {
  const ActivityOpenToPublicMap = buildFilteredMap(
    ActivityOpenToPublic,
    _ActivityOpenToPublicMappings
  )
  return (): Record<ActivityOpenToPublicType, string> =>
    ActivityOpenToPublicMap as Record<ActivityOpenToPublicType, string>
})()

// Getter for all activities that can be DISPLAYED (including potential old ones)
export const getActivityLabel = (() => {
  const DisplayableActivityMap = buildFilteredMap(
    DisplayableActivity,
    _DisplayableActivityMappings
  )
  return (label: DisplayableActivityType): string =>
    DisplayableActivityMap[label]
})()
