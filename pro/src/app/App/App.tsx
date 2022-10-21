import { setUser as setSentryUser } from '@sentry/browser'
import React, { useEffect } from 'react'
import { useSelector } from 'react-redux'
import { useLocation, Redirect } from 'react-router-dom'

import { useConfigureAnalytics } from 'hooks/useAnalytics'
import useCurrentUser from 'hooks/useCurrentUser'
import { RedirectToMaintenance } from 'new_components/RedirectToMaintenance'
import { useIsRoutePublic } from 'routes/hooks'
import { maintenanceSelector } from 'store/selectors/maintenanceSelector'

interface IAppProps {
  children: JSX.Element
}

const App = ({ children }: IAppProps): JSX.Element | null => {
  const { currentUser } = useCurrentUser()
  const location = useLocation()
  const isMaintenanceActivated = useSelector(maintenanceSelector)
  const [isRoutePublic, fromUrl] = useIsRoutePublic()

  useConfigureAnalytics(currentUser?.nonHumanizedId)

  useEffect(() => {
    window.scrollTo(0, 0)
  }, [location.pathname])

  if (currentUser !== null) {
    setSentryUser({ id: currentUser.id })
  } else if (!isRoutePublic) {
    const loginUrl = fromUrl.includes('logout')
      ? '/connexion'
      : `/connexion?de=${fromUrl}`
    return <Redirect to={loginUrl} />
  }

  if (isMaintenanceActivated) {
    return <RedirectToMaintenance />
  }

  return children
}

export default App
