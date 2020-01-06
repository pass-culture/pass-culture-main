import PropTypes from 'prop-types'
import React, { Fragment } from 'react'
import Helmet from 'react-helmet'
import { matchPath, Route } from 'react-router-dom'

import ErrorCatcherContainer from '../components/layout/ErrorCatcher/ErrorCatcherContainer'
import MenuContainer from '../components/layout/Menu/MenuContainer'
import Notifications from '../components/layout/Notifications/Notifications'
import OverlayContainer from '../components/layout/Overlay/OverlayContainer'
import SharePopinContainer from '../components/layout/Share/SharePopinContainer'
import SplashContainer from '../components/layout/Splash/SplashContainer'
import browserRoutes from '../components/router/browserRoutes'
import { IS_DEV, PROJECT_NAME } from '../utils/config'
import RedirectToMaintenance from './RedirectToMaintenance'

const getPageTitle = obj => `${obj && obj.title ? `${obj.title} - ` : ''}`

const getCurrentRouteObjectByPath = (entries, locpathname) =>
  (entries && entries.filter(obj => obj && matchPath(locpathname, obj))[0]) || null

const getBodyClass = obj => {
  const path = (obj && obj.path.split('/').filter(v => v)[0]) || ''
  return `page-${path || 'home'}`
}

export const App = ({ children, history, location, isMaintenanceActivated }) => {
  if (isMaintenanceActivated) {
    return <RedirectToMaintenance />
  } else {
    const currentRouteObj = getCurrentRouteObjectByPath(browserRoutes, location.pathname)
    const bodyClass = getBodyClass(currentRouteObj)
    const pageTitle = getPageTitle(currentRouteObj)
    return (
      <Fragment>
        <Helmet>
          <body className={`web ${bodyClass}`} />
          <title>
            {`${pageTitle}${PROJECT_NAME}${(IS_DEV && ' | DEV') || ''}`}
          </title>
        </Helmet>
        <ErrorCatcherContainer>
          {children}
          <OverlayContainer />
          <Route
            component={MenuContainer}
            history={history}
            path="*/menu"
          />
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
  history: PropTypes.shape().isRequired,
  isMaintenanceActivated: PropTypes.bool.isRequired,
  location: PropTypes.shape().isRequired,
}
