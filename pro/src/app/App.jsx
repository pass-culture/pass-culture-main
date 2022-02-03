import { setUser } from '@sentry/browser'
import PropTypes from 'prop-types'
import React, { useEffect, useState } from 'react'
import { matchPath } from 'react-router'

import Spinner from 'components/layout/Spinner'
import routes, { routesWithMain } from 'utils/routes_map'

import RedirectToMaintenance from './RedirectToMaintenance'

export const App = props => {
  const {
    children,
    currentUser,
    isFeaturesInitialized,
    getCurrentUser,
    history,
    isMaintenanceActivated,
    loadFeatures,
    location,
    isUserInitialized,
  } = props

  const [isReady, setIsReady] = useState(false)
  const currentPathname = window.location.pathname

  useEffect(() => {
    if (!isFeaturesInitialized) {
      loadFeatures()
    }
  }, [isFeaturesInitialized, loadFeatures])

  useEffect(() => {
    if (!isUserInitialized && !currentUser) {
      getCurrentUser()
    }

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
      setUser({ id: currentUser.pk })
      setIsReady(true)
    }
  }, [
    currentUser,
    currentPathname,
    getCurrentUser,
    history,
    location,
    isUserInitialized,
  ])

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

App.propTypes = {
  children: PropTypes.oneOfType([
    PropTypes.arrayOf(PropTypes.shape()),
    PropTypes.shape(),
  ]).isRequired,
  getCurrentUser: PropTypes.func.isRequired,
  isFeaturesInitialized: PropTypes.bool.isRequired,
  isMaintenanceActivated: PropTypes.bool.isRequired,
  isUserInitialized: PropTypes.bool.isRequired,
  loadFeatures: PropTypes.func.isRequired,
}
