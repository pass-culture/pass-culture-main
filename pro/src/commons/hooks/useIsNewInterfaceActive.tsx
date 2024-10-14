import { useSelector } from 'react-redux'

import { selectCurrentUser } from 'commons/store/user/selectors'
import { formatBrowserTimezonedDateAsUTC } from 'commons/utils/date'

export const useIsNewInterfaceActive = (): boolean => {
  const currentUser = useSelector(selectCurrentUser)

  return (
    !!currentUser?.navState?.newNavDate &&
    new Date(currentUser.navState.newNavDate) <=
      new Date(formatBrowserTimezonedDateAsUTC(new Date()))
  )
}
