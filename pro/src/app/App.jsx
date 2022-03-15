import { setUser as setSentryUser } from '@sentry/browser'
import PropTypes from 'prop-types'
import React, { useEffect, useState } from 'react'
import { matchPath } from 'react-router'

import useCurrentUser from 'components/hooks/useCurrentUser'
import Spinner from 'components/layout/Spinner'
import { useFeature } from 'hooks'
import routes, { routesWithMain } from 'utils/routes_map'

import RedirectToMaintenance from './RedirectToMaintenance'

export const App = props => {
  const { children, history, isMaintenanceActivated, location } = props

  const [isReady, setIsReady] = useState(false)
  const { isUserInitialized, currentUser } = useCurrentUser()
  const currentPathname = window.location.pathname

  const { initialized: isFeaturesInitialized } = useFeature()

  useEffect(() => {
    if (isUserInitialized && !currentUser) {
      const publicRouteList = [...routes, ...routesWithMain].filter(
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

  if (!isReady || !isUserInitialized || !isFeaturesInitialized) {
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
  history: PropTypes.shape().isRequired,
  isMaintenanceActivated: PropTypes.bool.isRequired,
  location: PropTypes.shape().isRequired,
}
