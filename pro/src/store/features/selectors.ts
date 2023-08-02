import { createSelector } from '@reduxjs/toolkit'

import { RootState } from 'store/reducers'

export const isFeatureActive = (
  state: RootState,
  featureName: string
): boolean => {
  if (featureName === null) {
    return true
  }

  const features = state.features.list
  if (!features) {
    return false
  }

  const currentFeature = features.find(
    feature => feature.nameKey === featureName
  )
  return Boolean(currentFeature?.isActive)
}

const selectFeatures = (state: RootState) => state.features.list

export const selectActiveFeatures = createSelector(selectFeatures, features =>
  features.filter(feature => feature.isActive).map(({ name }) => name)
)
