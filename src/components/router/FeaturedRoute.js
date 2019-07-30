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
    const { areFeaturesLoaded, disabled, ...routeProps } = this.props
    const { path } = routeProps

    if (!areFeaturesLoaded) {
      return null
    }

    if (disabled) {
      return (<Route
        component={NotMatch}
        path={path}
              />)
    }

    return <Route {...routeProps} />
  }
}

FeaturedRoute.propTypes = {
  areFeaturesLoaded: PropTypes.bool.isRequired,
  disabled: PropTypes.bool.isRequired,
  requestGetFeatures: PropTypes.func.isRequired,
}

export default FeaturedRoute
