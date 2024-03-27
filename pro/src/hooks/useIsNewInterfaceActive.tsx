import { useSelector } from 'react-redux'

import { selectCurrentUser } from 'store/user/selectors'
import { formatBrowserTimezonedDateAsUTC } from 'utils/date'

import useActiveFeature from './useActiveFeature'

const useIsNewInterfaceActive = (): boolean => {
  const currentUser = useSelector(selectCurrentUser)
  const isNewNavActive = useActiveFeature('WIP_ENABLE_PRO_SIDE_NAV')

  return (
    isNewNavActive &&
    !!currentUser?.navState?.newNavDate &&
    new Date(currentUser.navState.newNavDate) <=
      new Date(formatBrowserTimezonedDateAsUTC(new Date()))
  )
}

export default useIsNewInterfaceActive
