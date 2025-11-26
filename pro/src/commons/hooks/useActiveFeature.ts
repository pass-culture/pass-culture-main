import { isFeatureActive } from '@/commons/store/features/selectors'
import type { RootState } from '@/commons/store/store'

import { useAppSelector } from './useAppSelector'

export const useActiveFeature = (featureName: string): boolean => {
  const isActive = useAppSelector((state: RootState) =>
    isFeatureActive(state, featureName)
  )

  return isActive
}
