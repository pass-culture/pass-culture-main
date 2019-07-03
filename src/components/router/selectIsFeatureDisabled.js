import createCachedSelector from 're-reselect'

const mapArgsToCacheKey = (state, featureName) => featureName || ''

const selectIsFeatureDisabled = createCachedSelector(
  state => state.data.features,
  (state, featureName) => featureName,
  (features, featureName) => {
    if (!features) {
      return true
    }

    if (!featureName) {
      return false
    }

    const selectedFeature = features.find(
      feature => feature.name === featureName
    )

    if (!selectedFeature) {
      return false
    }

    return !selectedFeature.isActive
  }
)(mapArgsToCacheKey)

export default selectIsFeatureDisabled
