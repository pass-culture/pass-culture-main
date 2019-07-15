import PropTypes from 'prop-types'
import React, { PureComponent } from 'react'
import { Route } from 'react-router-dom'

import NotMatch from '../pages/NotMatch'

class FeaturedRoute extends PureComponent {
  componentDidMount() {
    const { features, requestGetFeatures } = this.props

    if (features) {
      return
    }

    requestGetFeatures()
  }

  render() {
    const { features, isFeatureDisabled, ...routeProps } = this.props

    if (!features) {
      return null
    }

    if (isFeatureDisabled) {
      return <Route component={NotMatch} />
    }

    return <Route {...routeProps} />
  }
}

FeaturedRoute.defaultProps = {
  features: null,
  isFeatureDisabled: true,
}

FeaturedRoute.propTypes = {
  features: PropTypes.arrayOf(PropTypes.shape()),
  isFeatureDisabled: PropTypes.bool,
  requestGetFeatures: PropTypes.func.isRequired,
}

export default FeaturedRoute
