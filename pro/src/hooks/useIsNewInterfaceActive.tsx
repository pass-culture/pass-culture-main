import { useSelector } from 'react-redux'

import { selectCurrentUser } from 'store/user/selectors'

import useActiveFeature from './useActiveFeature'

const useIsNewInterfaceActive = (): boolean => {
  const currentUser = useSelector(selectCurrentUser)
  const isNewNavActive = useActiveFeature('WIP_ENABLE_PRO_SIDE_NAV')

  return isNewNavActive && Boolean(currentUser?.navState?.newNavDate)
}

export default useIsNewInterfaceActive
