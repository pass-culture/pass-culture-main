import PropTypes from 'prop-types'
import React, { PureComponent } from 'react'
import { Route } from 'react-router-dom'

import ErrorsPage from '../layout/ErrorBoundaries/ErrorsPage/ErrorsPage'
import PageNotFoundContainer from '../layout/ErrorBoundaries/ErrorsPage/PageNotFound/PageNotFoundContainer'

class FeaturedRoute extends PureComponent {
  componentDidMount() {
    const { areFeaturesLoaded, requestGetFeatures } = this.props

    if (areFeaturesLoaded) {
      return
    }

    requestGetFeatures()
  }

  render() {
    const { areFeaturesLoaded, isRouteDisabled, ...routeProps } = this.props
    const { path } = routeProps

    if (!areFeaturesLoaded) {
      return null
    }

    if (isRouteDisabled) {
      return (<Route
        component={PageNotFoundContainer}
        path={path}
              />)
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
  isRouteDisabled: PropTypes.bool.isRequired,
  requestGetFeatures: PropTypes.func.isRequired,
}

export default FeaturedRoute
