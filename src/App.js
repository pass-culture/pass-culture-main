import React from 'react'
import PropTypes from 'prop-types'
import Helmet from 'react-helmet'
import { compose } from 'redux'
import { withRouter, matchPath } from 'react-router-dom'

import routes from './utils/routes'
import MainMenu from './components/menu'
import Debug from './components/layout/Debug'
import Splash from './components/layout/Splash'
import Overlay from './components/layout/Overlay'
import SharePopin from './components/share/SharePopin'
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
    <React.Fragment>
      <Helmet>
        <body className={`web ${bodyClass}`} />
        <title>
          {`${pageTitle}${PROJECT_NAME}${(IS_DEV && ' | DEV') || ''}`}
        </title>
      </Helmet>
      <Debug className="app is-relative">
        {children}
        <Overlay />
        <MainMenu />
        <Splash />
        <SharePopin />
        <img
          alt="beta"
          className="beta-corner is-overlay"
          src={`${ROOT_PATH}/beta.png`}
          srcSet={`${ROOT_PATH}/beta@2x.png`}
        />
      </Debug>
    </React.Fragment>
  )
}

App.propTypes = {
  children: PropTypes.node.isRequired,
  location: PropTypes.object.isRequired,
}

export default compose(withRouter)(App)
