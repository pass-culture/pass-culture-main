import PropTypes from 'prop-types'
import React, { Fragment } from 'react'
import Helmet from 'react-helmet'
import { matchPath } from 'react-router-dom'

import ErrorCatcher from '../../components/layout/ErrorBoundaries/ErrorCatcher/ErrorCatcher'
import NavBarContainer from '../../components/layout/NavBar/NavBarContainer'
import Notifications from '../../components/layout/Notifications/Notifications'
import OverlayContainer from '../../components/layout/Overlay/OverlayContainer'
import SharePopinContainer from '../../components/layout/Share/SharePopinContainer'
import SplashContainer from '../../components/layout/Splash/SplashContainer'
import routes from '../../components/router/routes'
import { IS_DEV, PROJECT_NAME } from '../../utils/config'
import { isPathWithNavBar } from './domain/isPathWithNavBar'
import RedirectToMaintenance from './RedirectToMaintenance/RedirectToMaintenance'
import { StatusBarHelmet } from './StatusBar/StatusBarHelmet'

const getPageTitle = obj => `${obj && obj.title ? `${obj.title} - ` : ''}`

const getCurrentRouteObjectByPath = (entries, locpathname) =>
  (entries && entries.filter(obj => obj && matchPath(locpathname, obj))[0]) || null

export const App = ({ children, location, isMaintenanceActivated, isUserConnected }) => {
  if (isMaintenanceActivated) {
    return <RedirectToMaintenance />
  } else {
    const isNavbarDisplayed = isPathWithNavBar(location.pathname) && isUserConnected
    const currentRouteObj = getCurrentRouteObjectByPath(routes, location.pathname)
    const pageTitle = getPageTitle(currentRouteObj)

    return (
      <Fragment>
        <Helmet>
          <title>
            {`${pageTitle}${PROJECT_NAME}${(IS_DEV && ' | DEV') || ''}`}
          </title>
        </Helmet>
        <StatusBarHelmet pathname={location.pathname} />
        {isNavbarDisplayed && <NavBarContainer
          path={location.pathname}
          routes={routes}
                              />}
        <ErrorCatcher>
          {children}
          <OverlayContainer />
          <SplashContainer />
          <SharePopinContainer />
          <Notifications />
        </ErrorCatcher>
      </Fragment>
    )
  }
}

App.propTypes = {
  children: PropTypes.node.isRequired,
  isMaintenanceActivated: PropTypes.bool.isRequired,
  location: PropTypes.shape().isRequired,
}
