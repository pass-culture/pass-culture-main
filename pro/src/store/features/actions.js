export const SET_FEATURES_IS_INITIALIZED = 'SET_FEATURE_IS_INITIALIZED'
export const SET_FEATURES = 'SET_FEATURES'

export const setIsInitialized = () => ({
  type: SET_FEATURES_IS_INITIALIZED,
})

export const setFeatures = features => ({
  features,
  type: SET_FEATURES,
})
