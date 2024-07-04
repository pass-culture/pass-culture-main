import { useActiveFeature } from './useActiveFeature'
import { useIsNewInterfaceActive } from './useIsNewInterfaceActive'

export const useWithoutFrame = (): boolean => {
  const isNewInterfaceActive = useIsNewInterfaceActive()
  const isWithoutFrame = useActiveFeature('WIP_ENABLE_PRO_WITHOUT_FRAME')

  return isNewInterfaceActive && isWithoutFrame
}
