export const SET_IS_INITIALIZED = 'SET_FEATURE_IS_INITIALIZED'
export const SET_FEATURES = 'SET_FEATURES'

export const setIsInitialized = () => ({
  type: SET_IS_INITIALIZED,
})

export const setFeatures = features => ({
  features,
  type: SET_FEATURES,
})
