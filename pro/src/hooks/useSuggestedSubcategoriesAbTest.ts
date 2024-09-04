import { useRemoteConfigParams } from 'app/App/analytics/firebase'

import { useActiveFeature } from './useActiveFeature'

export const useSuggestedSubcategoriesAbTest = (): boolean => {
  const { SUGGESTED_CATEGORIES: suggestedSubcategoriesRemoteConfig } =
    useRemoteConfigParams()

  const areSuggestedCategoriesEnabled = useActiveFeature(
    'WIP_SUGGESTED_SUBCATEGORIES'
  )
  const isInSuggestedSubcategoriesAbTest =
    suggestedSubcategoriesRemoteConfig === 'true'
  const areSuggestedSubcategoriesUsed =
    areSuggestedCategoriesEnabled && isInSuggestedSubcategoriesAbTest

  return areSuggestedSubcategoriesUsed
}
