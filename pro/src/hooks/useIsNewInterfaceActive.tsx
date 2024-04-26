import { useSelector } from 'react-redux'

import { selectCurrentUser } from 'store/user/selectors'
import { formatBrowserTimezonedDateAsUTC } from 'utils/date'

const useIsNewInterfaceActive = (): boolean => {
  const currentUser = useSelector(selectCurrentUser)

  return (
    !!currentUser?.navState?.newNavDate &&
    new Date(currentUser.navState.newNavDate) <=
      new Date(formatBrowserTimezonedDateAsUTC(new Date()))
  )
}

export default useIsNewInterfaceActive
