import { useEffect } from 'react'
import { useDispatch, useSelector } from 'react-redux'

import {
  isFeatureActive,
  selectFeaturesInitialized,
} from 'store/features/selectors'
import { loadFeatures } from 'store/features/thunks'

const useActiveFeature = featureName => {
  const isActive = useSelector(state => isFeatureActive(state, featureName))
  const isFeaturesInitialized = useSelector(state =>
    selectFeaturesInitialized(state)
  )

  const dispatch = useDispatch()
  useEffect(() => {
    if (!isFeaturesInitialized) {
      dispatch(loadFeatures())
    }
  }, [dispatch, isFeaturesInitialized])

  return isActive
}

export default useActiveFeature
