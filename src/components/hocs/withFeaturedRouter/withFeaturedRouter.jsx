import PropTypes from 'prop-types'
import React, { Component } from 'react'
import { connect } from 'react-redux'
import { withRouter } from 'react-router-dom'
import { compose } from 'redux'
import { requestData } from 'redux-saga-data'

import selectCurrentPathnameFeature from './selectCurrentPathnameFeature'
import NotMatch from '../../pages/NotMatch'

const withFeaturedRouter = WrappedComponent => {
  class _withFeaturedRouter extends Component {
    componentDidMount () {
      const { requestGetFeatures } = this.props
      requestGetFeatures()
    }

    render () {
      const { currentPathnameFeature, hasReceivedFeatures } = this.props
      const { isActive } = currentPathnameFeature || {}
      if (!hasReceivedFeatures) {
        return null
      }

      if (currentPathnameFeature && !isActive) {
        return <NotMatch />
      }

      return <WrappedComponent {...this.props} />
    }
  }

  const mapStateToProps = (state, ownProps) => {
    const { location: { pathname } } = ownProps
    return {
      currentPathnameFeature: selectCurrentPathnameFeature(state, pathname),
      hasReceivedFeatures: state.data.features !== null
    }
  }

  const mapDispatchToProps = dispatch => ({
    requestGetFeatures: () => dispatch(
      requestData({ apiPath: '/features' })
    )
  })

  _withFeaturedRouter.propTypes = {
    location: PropTypes.shape().isRequired
  }

  return compose(
    withRouter,
    connect(mapStateToProps, mapDispatchToProps)
  )(_withFeaturedRouter)
}

export default withFeaturedRouter
