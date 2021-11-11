import { useEffect } from 'react'
import { useDispatch, useSelector } from 'react-redux'

import { isFeatureActive, featuresInitialized } from 'store/features/selectors'
import { loadFeatures } from 'store/features/thunks'

const useActiveFeature = featureName => {
  const isActive = useSelector(state => isFeatureActive(state, featureName))
  const featuresAreInitialized = useSelector(state => featuresInitialized(state))

  const dispatch = useDispatch()
  useEffect(() => {
    if (!featuresAreInitialized) {
      dispatch(loadFeatures())
    }
  }, [dispatch, featuresAreInitialized])

  return isActive
}

export default useActiveFeature
