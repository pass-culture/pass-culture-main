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
    featuresAreInitialized,
    getCurrentUser,
    history,
    isMaintenanceActivated,
    loadFeatures,
    location,
  } = props

  const [isBusy, setIsBusy] = useState(false)
  const currentPathname = window.location.pathname

  useEffect(() => {
    if (!featuresAreInitialized) {
      loadFeatures()
    }
  }, [featuresAreInitialized, loadFeatures])

  useEffect(() => {
    const publicRouteList = [...routes, ...routesWithMain].filter(
      route => route.meta && route.meta.public
    )
    const isPublicRoute = !!publicRouteList.find(route => matchPath(currentPathname, route))

    if (!currentUser) {
      setIsBusy(true)
      getCurrentUser({
        handleSuccess: () => {
          setIsBusy(false)
        },
        handleFail: () => {
          if (!isPublicRoute) {
            const fromUrl = encodeURIComponent(`${location.pathname}${location.search}`)
            history.push(`/connexion?de=${fromUrl}`)
          }
          setIsBusy(false)
        },
      })
    }
    if (currentUser) {
      setUser({ id: currentUser.pk })
    }
  }, [currentUser, currentPathname, getCurrentUser, history, location])

  useEffect(() => {
    window.scrollTo(0, 0)
  }, [currentPathname])

  if (isMaintenanceActivated) {
    return <RedirectToMaintenance />
  }

  if (isBusy) {
    return (
      <main className="spinner-container">
        <Spinner />
      </main>
    )
  }

  return children
}

App.propTypes = {
  children: PropTypes.oneOfType([PropTypes.arrayOf(PropTypes.shape()), PropTypes.shape()])
    .isRequired,
  featuresInitialized: PropTypes.bool.isRequired,
  getCurrentUser: PropTypes.func.isRequired,
  isMaintenanceActivated: PropTypes.bool.isRequired,
  loadFeatures: PropTypes.func.isRequired,
}
