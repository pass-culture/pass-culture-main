import { isFeatureActive } from 'commons/store/features/selectors'
import { RootState } from 'commons/store/rootReducer'
import { useSelector } from 'react-redux'

export const useActiveFeature = (featureName: string): boolean => {
  const isActive = useSelector((state: RootState) =>
    isFeatureActive(state, featureName)
  )

  return isActive
}
