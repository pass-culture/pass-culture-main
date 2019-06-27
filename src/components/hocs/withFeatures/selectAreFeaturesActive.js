import { createSelector } from 'reselect'

const selectAreFeaturesActive = createSelector(
  state => state.data.features,
  (state, featureNames) => featureNames,
  (features, featureNames) =>
    !featureNames ||
    featureNames
      .map(featureName =>
        (features || []).find(feature => feature.name === featureName)
      )
      .every(feature => feature && feature.isActive)
)

export default selectAreFeaturesActive
