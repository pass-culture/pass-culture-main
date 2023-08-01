import { createSelector } from '@reduxjs/toolkit'

export const isFeatureActive = (state, featureName) => {
  if (featureName === null) {
    return true
  }

  const features = state.features.list
  if (features) {
    const currentFeature = features.find(
      feature => feature.nameKey === featureName
    )
    if (currentFeature) {
      return currentFeature.isActive
    }
    return false
  }
}

export const selectFeaturesInitialized = state => state.features.initialized

const selectFeatures = state => state.features.list

export const selectActiveFeatures = createSelector(selectFeatures, features =>
  features.filter(feature => feature.isActive).map(({ name }) => name)
)
