import get from 'lodash.get'

const isFeatureActive = (featureName) => get(window.features, featureName, false)

export default isFeatureActive
