import { setUser as setSentryUser } from '@sentry/browser'
import React, { useEffect } from 'react'
import { useSelector } from 'react-redux'
import { useLocation } from 'react-router-dom'

import Notification from 'components/Notification/Notification'
import { useConfigureFirebase } from 'hooks/useAnalytics'
import useCurrentUser from 'hooks/useCurrentUser'
import useLogNavigation from 'hooks/useLogNavigation'
import { maintenanceSelector } from 'store/selectors/maintenanceSelector'
import { URL_FOR_MAINTENANCE } from 'utils/config'

export interface IAppProps {
  children: JSX.Element
}

const App = ({ children }: IAppProps): JSX.Element | null => {
  const { currentUser } = useCurrentUser()
  const location = useLocation()
  const isMaintenanceActivated = useSelector(maintenanceSelector)
  useConfigureFirebase(currentUser?.nonHumanizedId)
  useLogNavigation()

  useEffect(() => {
    window.scrollTo(0, 0)
  }, [location.pathname])

  if (currentUser !== null) {
    setSentryUser({ id: currentUser.id })
  }

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
