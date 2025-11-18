// Back-End Model Enums
import { OnboardingActivity } from '@/apiClient/v1/models/OnboardingActivityWIP'
// Client Mappings
import { _OnboardingActivityMappings } from '@/commons/mappings/OnboardingActivity'

import { buildFilteredMap } from './utils/buildFilteredMap'

export const OnboardingActivityMap = buildFilteredMap(
  OnboardingActivity,
  _OnboardingActivityMappings
)
