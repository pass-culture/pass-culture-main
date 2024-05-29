import { useSelector } from 'react-redux'

import { isFeatureActive } from 'store/features/selectors'
import { RootState } from 'store/rootReducer'

export const useActiveFeature = (featureName: string): boolean => {
  const isActive = useSelector((state: RootState) =>
    isFeatureActive(state, featureName)
  )

  return isActive
}
