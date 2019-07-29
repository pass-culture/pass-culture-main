import createCachedSelector from 're-reselect'

const mapArgsToCacheKey = (state, featureName) => featureName || ''

const selectIsFeatureDisabled = createCachedSelector(
  state => state.data.features,
  (state, featureName) => featureName,
  (features, featureName) => {
    if (features.length === 0) {
      return true
    }

    if (!featureName) {
      return false
    }

    const selectedFeature = features.find(feature =>
      feature.nameKey === featureName)
    if (!selectedFeature) {
      return true
    }

    return !selectedFeature.isActive
  }
)(mapArgsToCacheKey)

export default selectIsFeatureDisabled
