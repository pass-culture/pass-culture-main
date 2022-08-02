import { setUser as setSentryUser } from '@sentry/browser'
import PropTypes from 'prop-types'
import React, { useEffect, useState } from 'react'
import { matchPath } from 'react-router'
import { useHistory, useLocation } from 'react-router-dom'

import { useConfigureAnalytics } from 'components/hooks/useAnalytics'
import useCurrentUser from 'components/hooks/useCurrentUser'
import Spinner from 'components/layout/Spinner'
import { RedirectToMaintenance } from 'new_components/RedirectToMaintenance'
import routes, { routesWithoutLayout } from 'utils/routes_map'

export const App = props => {
  const {
    children,
    isFeaturesInitialized,
    isMaintenanceActivated,
    loadFeatures,
  } = props
  const [isReady, setIsReady] = useState(false)
  const { isUserInitialized, currentUser } = useCurrentUser()
  const currentPathname = window.location.pathname
  const history = useHistory()
  const location = useLocation()
  useConfigureAnalytics(currentUser?.id)

  useEffect(() => {
    if (!isFeaturesInitialized) {
      loadFeatures()
    }
  }, [isFeaturesInitialized, loadFeatures])

  useEffect(() => {
    if (isUserInitialized && !currentUser) {
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
      }
      setIsReady(true)
    }

    if (isUserInitialized && currentUser) {
      setSentryUser({ id: currentUser.id })
      setIsReady(true)
    }
  }, [currentUser, currentPathname, history, location, isUserInitialized])

  useEffect(() => {
    window.scrollTo(0, 0)
  }, [currentPathname])

  if (isMaintenanceActivated) {
    return <RedirectToMaintenance />
  }

  if (!isReady || !isUserInitialized) {
    return (
      <main className="spinner-container">
        <Spinner />
      </main>
    )
  }

  return children
}

App.propTypes = {
  children: PropTypes.oneOfType([
    PropTypes.arrayOf(PropTypes.shape()),
    PropTypes.shape(),
  ]).isRequired,
  isFeaturesInitialized: PropTypes.bool.isRequired,
  isMaintenanceActivated: PropTypes.bool.isRequired,
  loadFeatures: PropTypes.func.isRequired,
}
