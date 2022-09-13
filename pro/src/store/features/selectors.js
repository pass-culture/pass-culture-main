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

export const selectActiveFeatures = state =>
  state.features.list
    .filter(feature => feature.isActive)
    .map(({ name }) => name)
