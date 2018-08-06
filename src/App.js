import React from 'react'
import PropTypes from 'prop-types'
import Helmet from 'react-helmet'
import { withRouter, matchPath } from 'react-router-dom'

import routes from './utils/routes'
import Debug from './components/layout/Debug'
import Splash from './components/layout/Splash'
import { ROOT_PATH, IS_DEV, PROJECT_NAME } from './utils/config'

const getPageTitle = obj => `${obj.title ? `${obj.title} - ` : ''}`

const getCurrentRouteObjectByPath = locpathname =>
  routes.filter(obj => matchPath(locpathname, obj))[0] || null

const getBodyClass = obj => {
  const path = (obj && obj.path.split('/').filter(v => v)[0]) || ''
  return `page-${path || 'home'}`
}

const App = ({ location, children }) => {
  const currentRouteObj = getCurrentRouteObjectByPath(location.pathname)
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
      <Debug className="app">
        {children}
        <img
          alt="beta"
          className="beta"
          src={`${ROOT_PATH}/beta.png`}
          srcSet={`${ROOT_PATH}/beta@2x.png`}
        />
        <Splash />
      </Debug>
    </React.Fragment>
  )
}

App.propTypes = {
  children: PropTypes.node.isRequired,
  location: PropTypes.object.isRequired,
}

export default withRouter(App)
