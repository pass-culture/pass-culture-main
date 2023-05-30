// import { setUser as setSentryUser } from '@sentry/browser'
import React from 'react'
import { useSelector } from 'react-redux'

import Notification from 'components/Notification/Notification'
import { useConfigureFirebase } from 'hooks/useAnalytics'
import useCurrentUser from 'hooks/useCurrentUser'
import useLogNavigation from 'hooks/useLogNavigation'
import usePageTitle from 'hooks/usePageTitle'
import { maintenanceSelector } from 'store/selectors/maintenanceSelector'
import { URL_FOR_MAINTENANCE } from 'utils/config'

interface AppProps {
  children: JSX.Element
}

const App = ({ children }: AppProps): JSX.Element | null => {
  const { currentUser } = useCurrentUser()

  const isMaintenanceActivated = useSelector(maintenanceSelector)
  useConfigureFirebase(currentUser?.nonHumanizedId)
  usePageTitle()
  useLogNavigation()

  // if (currentUser !== null) {
  //   setSentryUser({ id: currentUser.id })
  // }

  if (isMaintenanceActivated) {
    window.location.href = URL_FOR_MAINTENANCE
    return null
  }

  return (
    <>
      {children}
      <Notification />
    </>
  )
}

export default App
