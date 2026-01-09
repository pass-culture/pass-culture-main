// Back-End Model Enums

import { ActivityNotOpenToPublic } from '@/apiClient/v1/models/ActivityNotOpenToPublic'
import { ActivityOpenToPublic } from '@/apiClient/v1/models/ActivityOpenToPublic'
import { DisplayableActivity } from '@/apiClient/v1/models/DisplayableActivity'

import { _ActivityNotOpenToPublicMappings } from './ActivityNotOpenToPublic'
import { _ActivityOpenToPublicMappings } from './ActivityOpenToPublic'
// Client Mappings
import {
  _DisplayableActivityMappings,
  type DisplayableActivityType,
} from './DisplayableActivity'
import { buildFilteredMap } from './utils/buildFilteredMap'

// Getter for all activities that can be CHOSEN during structure registration or edition
export const getActivities = (() => {
  const ActivityOpenToPublicMap = buildFilteredMap(
    ActivityOpenToPublic,
    _ActivityOpenToPublicMappings,
    'ActivityOpenToPublic'
  )

  const ActivityNotOpenToPublicMap = buildFilteredMap(
    ActivityNotOpenToPublic,
    _ActivityNotOpenToPublicMappings,
    'ActivityNotOpenToPublic'
  )

  type ActivityMap<T extends 'OPEN_TO_PUBLIC' | 'NOT_OPEN_TO_PUBLIC'> =
    T extends 'OPEN_TO_PUBLIC'
      ? typeof ActivityOpenToPublicMap
      : typeof ActivityNotOpenToPublicMap

  return function getActivities<
    T extends 'OPEN_TO_PUBLIC' | 'NOT_OPEN_TO_PUBLIC',
  >(listType: T): ActivityMap<T> {
    return (
      listType === 'OPEN_TO_PUBLIC'
        ? ActivityOpenToPublicMap
        : ActivityNotOpenToPublicMap
    ) as ActivityMap<T>
  }
})()

// Getter for all activities that can be DISPLAYED (including potential old ones)
export const getActivityLabel = (() => {
  const DisplayableActivityMap = buildFilteredMap(
    DisplayableActivity,
    _DisplayableActivityMappings,
    'DisplayableActivity'
  )
  return (label: DisplayableActivityType): string =>
    DisplayableActivityMap[label]
})()
