import PropTypes from 'prop-types'
import React, { Component } from 'react'
import { BrowserRouter } from 'react-router-dom'

import { getFeaturedRoutes } from './utils'

class FeaturedBrowserRouter extends Component {
  componentDidMount() {
    const { features, requestGetFeatures } = this.props

    if (features) {
      return
    }

    requestGetFeatures()
  }

  render() {
    const { features, render } = this.props

    if (!features) {
      return null
    }

    const routes = getFeaturedRoutes(features)

    return <BrowserRouter>{render(routes)}</BrowserRouter>
  }
}

FeaturedBrowserRouter.defaultProps = {
  features: null,
}

FeaturedBrowserRouter.propTypes = {
  features: PropTypes.arrayOf(PropTypes.shape()),
  render: PropTypes.func.isRequired,
  requestGetFeatures: PropTypes.func.isRequired,
}

export default FeaturedBrowserRouter
