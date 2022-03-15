import { useEffect } from 'react'
import { useDispatch, useSelector } from 'react-redux'

import {
  selectFeaturesInitialized,
  selectFeatureList,
} from 'store/features/selectors'
import { loadFeatures } from 'store/features/thunks'

import { IFeatureList, IUseFeature } from './types'

const featureList: IFeatureList = {
  initialized: false,
  list: [],
}

const useFeature = (featureName: string): IUseFeature => {
  // FIXME: remove dispatch when all call to selectors.isFeatureActive have been changed by useFeature
  const dispatch = useDispatch()
  const isFeaturesInitialized = useSelector(state =>
    selectFeaturesInitialized(state)
  )
  const storeFeatures = useSelector(state => selectFeatureList(state))
  useEffect(() => {
    if (!isFeaturesInitialized) {
      // FIXME: when all call to selectors.isFeatureActive have been changed by useFeature
      // replace loadFeatures() api/api
      dispatch(loadFeatures())
    } else if (!featureList.initialized) {
      featureList.list = storeFeatures
      featureList.initialized = true
    }
  }, [dispatch, isFeaturesInitialized, storeFeatures])

  const isFeatureActive = (name: string) => {
    if (!featureList.initialized) {
      return
    }
    const feature = featureList.list.find(f => f.nameKey === name)
    return feature ? feature.isActive : undefined
  }

  return {
    initialized: featureList.initialized,
    isActive: !featureName || isFeatureActive(featureName),
  }
}

export default useFeature
