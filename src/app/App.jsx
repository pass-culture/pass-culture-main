import classnames from 'classnames'
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
    getCurrentUser,
    history,
    isMaintenanceActivated,
    location,
    modalOpen,
  } = props

  const [isBusy, setIsBusy] = useState(false)
  useEffect(() => {
    const publicRouteList = [...routes, ...routesWithMain].filter(
      route => route.meta && route.meta.public
    )
    const isPublicRoute = !!publicRouteList.find(route =>
      matchPath(window.location.pathname, route)
    )
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
  }, [currentUser, getCurrentUser, history, location])

  if (isMaintenanceActivated) {
    return <RedirectToMaintenance />
  }

  if (isBusy) {
    return <Spinner />
  }

  return (
    <div className={classnames('app', { 'modal-open': modalOpen })}>
      {children}
    </div>
  )
}

App.propTypes = {
  children: PropTypes.oneOfType([PropTypes.arrayOf(PropTypes.shape()), PropTypes.shape()])
    .isRequired,
  isMaintenanceActivated: PropTypes.bool.isRequired,
  modalOpen: PropTypes.bool.isRequired,
}
