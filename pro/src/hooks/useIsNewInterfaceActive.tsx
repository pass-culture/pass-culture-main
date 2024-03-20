import useActiveFeature from './useActiveFeature'
import useCurrentUser from './useCurrentUser'

const useIsNewInterfaceActive = (): boolean => {
  const { currentUser } = useCurrentUser()
  const isNewNavActive = useActiveFeature('WIP_ENABLE_PRO_SIDE_NAV')

  return isNewNavActive && Boolean(currentUser?.navState?.newNavDate)
}

export default useIsNewInterfaceActive
