import { useSelector } from 'react-redux'

import { isFeatureActive } from 'store/features/selectors'

const useActiveFeature = (featureName: string): boolean => {
  const isActive = useSelector(state => isFeatureActive(state, featureName))

  return isActive
}

export default useActiveFeature
