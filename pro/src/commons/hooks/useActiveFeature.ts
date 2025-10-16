import { useSelector } from 'react-redux'

import { isFeatureActive } from '@/commons/store/features/selectors'
import type { RootState } from '@/commons/store/store'

export const useActiveFeature = (featureName: string): boolean => {
  const isActive = useSelector((state: RootState) =>
    isFeatureActive(state, featureName)
  )

  return isActive
}
