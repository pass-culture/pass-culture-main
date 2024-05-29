import { useSelector } from 'react-redux'

import { selectCurrentUser } from 'store/user/selectors'
import { formatBrowserTimezonedDateAsUTC } from 'utils/date'

export const useIsNewInterfaceActive = (): boolean => {
  const currentUser = useSelector(selectCurrentUser)

  return (
    !!currentUser?.navState?.newNavDate &&
    new Date(currentUser.navState.newNavDate) <=
      new Date(formatBrowserTimezonedDateAsUTC(new Date()))
  )
}
