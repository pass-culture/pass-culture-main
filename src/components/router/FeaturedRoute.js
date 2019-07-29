import PropTypes from 'prop-types'
import React, { PureComponent } from 'react'
import { Route } from 'react-router-dom'

import NotMatch from '../pages/NotMatch'

class FeaturedRoute extends PureComponent {
  componentDidMount() {
    const { areFeaturesLoaded, requestGetFeatures } = this.props

    if (areFeaturesLoaded) {
      return
    }

    requestGetFeatures()
  }

  render() {
    const { areFeaturesLoaded, isFeatureDisabled, ...routeProps } = this.props
    const { path } = routeProps

    if (!areFeaturesLoaded) {
      return null
    }

    if (isFeatureDisabled) {
      return (<Route
        component={NotMatch}
        path={path}
              />)
    }

    return <Route {...routeProps} />
  }
}

FeaturedRoute.defaultProps = {
  isFeatureDisabled: true,
}

FeaturedRoute.propTypes = {
  areFeaturesLoaded: PropTypes.bool.isRequired,
  isFeatureDisabled: PropTypes.bool,
  requestGetFeatures: PropTypes.func.isRequired,
}

export default FeaturedRoute
