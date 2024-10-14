import { VenueTypeCode } from 'apiClient/v1'
import { useRemoteConfigParams } from 'app/App/analytics/firebase'

import { useActiveFeature } from './useActiveFeature'

export const isRecordStore = (
  venues: { venueTypeCode: VenueTypeCode }[]
): boolean => {
  return venues.some(
    (venue) => venue.venueTypeCode === ('RECORD_STORE' as VenueTypeCode)
  )
}

export const useSuggestedSubcategoriesAbTest = (
  venues: { venueTypeCode: VenueTypeCode }[]
): boolean => {
  const { SUGGESTED_CATEGORIES: suggestedSubcategoriesRemoteConfig } =
    useRemoteConfigParams()

  const areSuggestedCategoriesEnabled = useActiveFeature(
    'WIP_SUGGESTED_SUBCATEGORIES'
  )
  const isInSuggestedSubcategoriesAbTest =
    suggestedSubcategoriesRemoteConfig === 'true' || isRecordStore(venues)
  const areSuggestedSubcategoriesUsed =
    areSuggestedCategoriesEnabled && isInSuggestedSubcategoriesAbTest

  return areSuggestedSubcategoriesUsed
}
