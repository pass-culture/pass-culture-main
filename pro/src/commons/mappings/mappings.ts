// Back-End Model Enums
import { DisplayedActivity } from '@/apiClient/v1/models/DisplayedActivity'
import { OnboardingActivity } from '@/apiClient/v1/models/OnboardingActivity'

// Client Mappings
import { _DisplayedActivityMappings } from './DisplayedActivity'
import { _OnboardingActivityMappings } from './OnboardingActivity'
//
import { buildFilteredMap } from './utils/buildFilteredMap'

// ts-unused-exports:disable-next-line
export const DisplayedActivityMap = buildFilteredMap(DisplayedActivity, _DisplayedActivityMappings) // biome-ignore format:.
export const OnboardingActivityMap = buildFilteredMap(OnboardingActivity, _OnboardingActivityMappings) // biome-ignore format:.
