// Back-End Model Enums

import { ActivityNotOpenToPublic } from '@/apiClient/v1/models/ActivityNotOpenToPublic'
import { ActivityOpenToPublic } from '@/apiClient/v1/models/ActivityOpenToPublic'
import { DisplayableActivity } from '@/apiClient/v1/models/DisplayableActivity'

import {
  _ActivityNotOpenToPublicMappings,
  type ActivityNotOpenToPublicType,
} from './ActivityNotOpenToPublic'
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

// Getter for all activities that can be CHOSEN during structure registration or edition if the structure is open to public
export const getActivities = (() => {
  const ActivityOpenToPublicMap = buildFilteredMap(
    ActivityOpenToPublic,
    _ActivityOpenToPublicMappings
  )
  return (): Record<ActivityOpenToPublicType, string> =>
    ActivityOpenToPublicMap as Record<ActivityOpenToPublicType, string>
})()

// Getter for all activities that can be CHOSEN during structure registration or edition if the structure is not open to public
export const getActivitiesNotOpenToPublic = (() => {
  const ActivityNotOpenToPublicMap = buildFilteredMap(
    ActivityNotOpenToPublic,
    _ActivityNotOpenToPublicMappings
  )
  return (): Record<ActivityNotOpenToPublicType, string> =>
    ActivityNotOpenToPublicMap as Record<ActivityNotOpenToPublicType, string>
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
