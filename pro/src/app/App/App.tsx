import { setUser as setSentryUser } from '@sentry/browser'
import React, { useEffect, useState } from 'react'
import { useSelector } from 'react-redux'
import { matchPath } from 'react-router'
import { useHistory, useLocation } from 'react-router-dom'

import { useConfigureAnalytics } from 'components/hooks/useAnalytics'
import useCurrentUser from 'components/hooks/useCurrentUser'
import Spinner from 'components/layout/Spinner'
import { RedirectToMaintenance } from 'new_components/RedirectToMaintenance'
import { maintenanceSelector } from 'store/selectors/maintenanceSelector'
import routes, { routesWithoutLayout } from 'utils/routes_map'

interface IAppProps {
  children: JSX.Element
}

const App = ({ children }: IAppProps): JSX.Element => {
  const { currentUser } = useCurrentUser()
  const currentPathname = window.location.pathname
  const history = useHistory()
  const location = useLocation()
  const isMaintenanceActivated = useSelector(maintenanceSelector)
  const [isReady, setIsReady] = useState(false)

  useConfigureAnalytics(currentUser?.id)

  useEffect(() => {
    if (currentUser !== null) {
      setSentryUser({ id: currentUser.id })
      setIsReady(true)
    }
  }, [currentUser])

  useEffect(() => {
    if (currentUser === null) {
      const publicRouteList = [...routes, ...routesWithoutLayout].filter(
        route => route.meta && route.meta.public
      )
      const isPublicRoute = !!publicRouteList.find(route =>
        matchPath(currentPathname, route)
      )

      if (!isPublicRoute) {
        const fromUrl = encodeURIComponent(
          `${location.pathname}${location.search}`
        )
        history.push(`/connexion?de=${fromUrl}`)
      } else {
        setIsReady(true)
      }
    }
  }, [currentUser, currentPathname, history, location])

  useEffect(() => {
    window.scrollTo(0, 0)
  }, [currentPathname])

  if (isMaintenanceActivated) {
    return <RedirectToMaintenance />
  }

  if (!isReady) {
    return (
      <main className="spinner-container">
        <Spinner />
      </main>
    )
  }

  return children
}

export default App
