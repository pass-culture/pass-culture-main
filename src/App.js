import PropTypes from 'prop-types'
import React, { Fragment } from 'react'
import Helmet from 'react-helmet'
import { matchPath, Route, withRouter } from 'react-router-dom'

import DebugContainer from './components/layout/Debug/DebugContainer'
import ErrorCatcherContainer from './components/layout/ErrorCatcher/ErrorCatcherContainer'
import browserRoutes from './components/router/browserRoutes'
import MenuContainer from './components/layout/Menu/MenuContainer'
import Notifications from './components/layout/notifications'
import OverlayContainer from './components/layout/Overlay/OverlayContainer'
import SharePopinContainer from './components/layout/Share/SharePopinContainer'
import Splash from './components/layout/Splash'
import { ROOT_PATH, IS_DEV, PROJECT_NAME } from './utils/config'

const getPageTitle = obj => `${obj && obj.title ? `${obj.title} - ` : ''}`

const getCurrentRouteObjectByPath = (entries, locpathname) =>
  (entries && entries.filter(obj => obj && matchPath(locpathname, obj))[0]) || null

const getBodyClass = obj => {
  const path = (obj && obj.path.split('/').filter(v => v)[0]) || ''
  return `page-${path || 'home'}`
}

const App = ({ children, history, location }) => {
  const currentRouteObj = getCurrentRouteObjectByPath(browserRoutes, location.pathname)
  const bodyClass = getBodyClass(currentRouteObj)
  const pageTitle = getPageTitle(currentRouteObj)
  return (
    <Fragment>
      <Helmet>
        <body className={`web ${bodyClass}`} />
        <title>{`${pageTitle}${PROJECT_NAME}${(IS_DEV && ' | DEV') || ''}`}</title>
      </Helmet>
      <DebugContainer className="app is-relative">
        <ErrorCatcherContainer>
          {/* TODO: mettre ici le composant from password */}
          {children}
          <OverlayContainer />
          <Route
            component={MenuContainer}
            history={history}
            path="*/menu"
          />
          <Splash />
          <SharePopinContainer />
          <Notifications />
          <img
            alt="beta"
            className="beta-corner is-overlay"
            src={`${ROOT_PATH}/beta.png`}
            srcSet={`${ROOT_PATH}/beta@2x.png`}
          />
        </ErrorCatcherContainer>
      </DebugContainer>
    </Fragment>
  )
}

App.propTypes = {
  children: PropTypes.node.isRequired,
  history: PropTypes.shape().isRequired,
  location: PropTypes.shape().isRequired,
}

export default withRouter(App)
