import get from 'lodash.get'

export const isFeatureDisabled = featureName => {
  const disabledFeatureByDefault = false
  const isFeatureActive = get(
    window.features,
    featureName,
    disabledFeatureByDefault
  )

  return !isFeatureActive
}
