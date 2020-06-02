import PropTypes from 'prop-types'
import React, { Fragment } from 'react'
import Helmet from 'react-helmet'
import { matchPath } from 'react-router-dom'

import ErrorCatcherContainer from '../../components/layout/ErrorCatcher/ErrorCatcherContainer'
import NavBar from '../../components/layout/NavBar/NavBar'
import Notifications from '../../components/layout/Notifications/Notifications'
import OverlayContainer from '../../components/layout/Overlay/OverlayContainer'
import SharePopinContainer from '../../components/layout/Share/SharePopinContainer'
import SplashContainer from '../../components/layout/Splash/SplashContainer'
import browserRoutes from '../../components/router/browserRoutes'
import { IS_DEV, PROJECT_NAME } from '../../utils/config'
import RedirectToMaintenance from './RedirectToMaintenance/RedirectToMaintenance'

const getPageTitle = obj => `${obj && obj.title ? `${obj.title} - ` : ''}`

const getCurrentRouteObjectByPath = (entries, locpathname) =>
  (entries && entries.filter(obj => obj && matchPath(locpathname, obj))[0]) || null

export const App = ({ children, location, isMaintenanceActivated }) => {
  if (isMaintenanceActivated) {
    return <RedirectToMaintenance />
  } else {
    const currentRouteObj = getCurrentRouteObjectByPath(browserRoutes, location.pathname)
    const pageTitle = getPageTitle(currentRouteObj)
    return (
      <Fragment>
        <Helmet>
          <title>
            {`${pageTitle}${PROJECT_NAME}${(IS_DEV && ' | DEV') || ''}`}
          </title>
        </Helmet>
        <ErrorCatcherContainer>
          {children}
          <NavBar path={location.pathname} />
          <OverlayContainer />
          <SplashContainer />
          <SharePopinContainer />
          <Notifications />
        </ErrorCatcherContainer>
      </Fragment>
    )
  }
}

App.propTypes = {
  children: PropTypes.node.isRequired,
  isMaintenanceActivated: PropTypes.bool.isRequired,
  location: PropTypes.shape().isRequired,
}
