import PropTypes from 'prop-types'
import React, { Component } from 'react'
import { connect } from 'react-redux'
import { requestData } from 'redux-saga-data'

import selectAreFeaturesActive from './selectAreFeaturesActive'
import NotMatch from '../../pages/NotMatch'

const withFeatures = config => WrappedComponent => {

  const { requiredFeatureNames } = config || {}

  class _withFeatures extends Component {
    componentDidMount () {
      const { requestGetFeatures } = this.props
      requestGetFeatures()
    }

    render () {
      const { areFeaturesActive, hasReceivedFeatures } = this.props
      if (!hasReceivedFeatures) {
        return null
      }

      if (requiredFeatureNames && !areFeaturesActive) {
        return <NotMatch />
      }

      return <WrappedComponent {...this.props} />
    }
  }

  const mapStateToProps = state => ({
      areFeaturesActive: selectAreFeaturesActive(state, requiredFeatureNames),
      hasReceivedFeatures: state.data.features !== null
  })

  const mapDispatchToProps = dispatch => ({
    requestGetFeatures: () => dispatch(
      requestData({ apiPath: '/features' })
    )
  })

  _withFeatures.propTypes = {
    areFeaturesActive: PropTypes.bool.isRequired,
    hasReceivedFeatures: PropTypes.bool.isRequired
  }

  return connect(mapStateToProps, mapDispatchToProps)(_withFeatures)
}

export default withFeatures
