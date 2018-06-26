import React, { Component } from 'react'
import { connect } from 'react-redux'
import { withRouter } from 'react-router'
import { compose } from 'redux'

import { requestData } from '../../reducers/data'
import createOccasionSelector from '../../selectors/createOccasion'
import { NEW } from '../../utils/config'
import { occasionNormalizer } from '../../utils/normalizers'

const withCurrentOccasion = WrappedComponent => {
  class _withCurrentOccasion extends Component {

    constructor () {
      super()
      this.state = {
        apiPath: null,
        isLoading: false,
        isNew: false,
        routePath: null
      }
    }

    handleDataRequest = () => {
      const {
        match: {
          params: {
            occasionId
          }
        },
        requestData,
      } = this.props
      const { apiPath } = this.state

      occasionId !== 'nouveau' && requestData(
        'GET',
        apiPath,
        {
          key: 'occasions',
          normalizer: occasionNormalizer
        }
      )
    }

    componentDidMount() {
      this.props.user && this.handleDataRequest()
    }

    componentDidUpdate(prevProps) {
      const { user } = this.props
      if (user && user !== prevProps.user) {
        this.handleDataRequest()
      }
    }

    static getDerivedStateFromProps (nextProps) {
      const {
        occasion,
        match: { params: { occasionId } },
      } = nextProps
      const {
        id
      } = (occasion || {})
      const isNew = occasionId === 'nouveau'
      const apiPath = `occasions${isNew ? '' : `/${occasionId}`}`
      const routePath = `/offres${isNew ? '' : `/${occasionId}`}`
      return {
        apiPath,
        isLoading: !(id || isNew),
        isNew,
        newMediationRoutePath: `${routePath}/accroches/nouveau`,
        occasionIdOrNew: isNew ? NEW : occasionId,
        routePath
      }
    }

    render () {
      return <WrappedComponent {...this.props} {...this.state} />
    }
  }

  const occasionSelector = createOccasionSelector()

  return compose(
    withRouter,
    connect(
      (state, ownProps) => ({
        occasion: occasionSelector(state, ownProps.match.params.occasionId),
        user: state.user,
      }),
      { requestData }
    )
  )(_withCurrentOccasion)
}

export default withCurrentOccasion
