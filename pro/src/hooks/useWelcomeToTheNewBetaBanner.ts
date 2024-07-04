import { useSelector } from 'react-redux'

import { selectCurrentUser } from 'store/user/selectors'
import { formatBrowserTimezonedDateAsUTC } from 'utils/date'

export const useWelcomeToTheNewBetaBanner = (): boolean => {
  const currentUser = useSelector(selectCurrentUser)

  if (currentUser?.navState?.newNavDate) {
    const dateNPP = new Date(
      formatBrowserTimezonedDateAsUTC(new Date(currentUser.navState.newNavDate))
    )
    const dateInscription = new Date(
      formatBrowserTimezonedDateAsUTC(new Date(currentUser.dateCreated))
    )
    const dateNPPForAllUsers = new Date('2024-07-09T00:00:00.000')

    return dateNPP >= dateNPPForAllUsers && dateInscription < dateNPPForAllUsers
  }

  return false
}
