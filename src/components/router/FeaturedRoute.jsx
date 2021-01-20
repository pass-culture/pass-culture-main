import PropTypes from 'prop-types'
import React, { PureComponent } from 'react'
import { Route } from 'react-router-dom'

import ErrorsPage from '../layout/ErrorBoundaries/ErrorsPage/ErrorsPage'
import PageNotFoundContainer from '../layout/ErrorBoundaries/ErrorsPage/PageNotFound/PageNotFoundContainer'

const PAGES_WORKING_WITHOUT_FEATURES = ['/', '', '/beta', '/verification-eligibilite']
class FeaturedRoute extends PureComponent {
  componentDidMount() {
    const { areFeaturesLoaded, requestGetFeatures, featuresFetchFailed } = this.props

    if (areFeaturesLoaded || featuresFetchFailed) {
      return
    }

    requestGetFeatures()
  }

  render() {
    const { areFeaturesLoaded, isRouteDisabled, featuresFetchFailed, ...routeProps } = this.props
    const { path } = routeProps
    const displayRoute =
      areFeaturesLoaded || (PAGES_WORKING_WITHOUT_FEATURES.includes(path) && featuresFetchFailed)

    if (!displayRoute) {
      return null
    }

    if (isRouteDisabled) {
      return (
        <Route
          component={PageNotFoundContainer}
          path={path}
        />
      )
    }

    return (
      <ErrorsPage>
        <Route {...routeProps} />
      </ErrorsPage>
    )
  }
}

FeaturedRoute.propTypes = {
  areFeaturesLoaded: PropTypes.bool.isRequired,
  featuresFetchFailed: PropTypes.bool.isRequired,
  isRouteDisabled: PropTypes.bool.isRequired,
  requestGetFeatures: PropTypes.func.isRequired,
}

export default FeaturedRoute
