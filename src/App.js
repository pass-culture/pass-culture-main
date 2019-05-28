import React, { Fragment } from 'react'
import PropTypes from 'prop-types'
import Helmet from 'react-helmet'
import { compose } from 'redux'
import { withRouter, matchPath, Route } from 'react-router-dom'

import routes from './utils/routes'
import MainMenu from './components/menu'
import DebugContainer from './components/layout/Debug/DebugContainer'
import Splash from './components/layout/Splash'
import Overlay from './components/layout/Overlay'
import Notifications from './components/layout/notifications'
import ErrorCatcherContainer from './components/layout/ErrorCatcher/ErrorCatcherContainer'
import { SharePopin } from './components/share/SharePopin'
import { getReactRoutes } from './utils/routes-utils'
import { ROOT_PATH, IS_DEV, PROJECT_NAME } from './utils/config'

const appRoutes = getReactRoutes(routes)

const getPageTitle = obj => `${obj && obj.title ? `${obj.title} - ` : ''}`

const getCurrentRouteObjectByPath = (entries, locpathname) =>
  (entries && entries.filter(obj => obj && matchPath(locpathname, obj))[0]) ||
  null

const getBodyClass = obj => {
  const path = (obj && obj.path.split('/').filter(v => v)[0]) || ''
  return `page-${path || 'home'}`
}

const App = ({ location, children }) => {
  const currentRouteObj = getCurrentRouteObjectByPath(
    appRoutes,
    location.pathname
  )
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
      <DebugContainer className="app is-relative">
        <ErrorCatcherContainer>
          {/* TODO: mettre ici le composant from password */}
          {children}
          <Overlay />
          <Route path="*/menu" component={MainMenu} />
          <Splash />
          <SharePopin />
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
  location: PropTypes.object.isRequired,
}

export default compose(withRouter)(App)
