import { createSelector } from '@reduxjs/toolkit'

import { RootState } from '@/commons/store/rootReducer'

export const isFeatureActive = (
  state: RootState,
  featureName: string
): boolean => {
  const features = state.features.list
  if (!Array.isArray(features)) {
    return false
  }
  const currentFeature = features.find(
    (feature) => feature.nameKey === featureName
  )
  return Boolean(currentFeature?.isActive)
}

const selectFeatures = (state: RootState) => state.features.list

export const selectActiveFeatures = createSelector(
  selectFeatures,
  (features) => {
    if (!Array.isArray(features)) {
      return []
    }
    return features
      .filter((feature) => feature.isActive)
      .map(({ name }) => name)
  }
)

export const selectLastLoaded = (state: RootState) => state.features.lastLoaded
