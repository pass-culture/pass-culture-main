import { requestData } from 'pass-culture-shared'
import React, { Component } from 'react'
import { connect } from 'react-redux'
import { withRouter } from 'react-router'
import { compose } from 'redux'

import occasionSelector from '../../selectors/occasion'
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
        occasion,
        requestData,
        user,
      } = this.props
      const { apiPath, isNew } = this.state
      user && !isNew  && !occasion && requestData(
        'GET',
        apiPath,
        {
          key: 'occasions',
          normalizer: occasionNormalizer
        }
      )
    }

    componentDidMount() {
      this.handleDataRequest()
    }

    componentDidUpdate(prevProps) {
      const { user } = this.props
      if (user && !prevProps.user) {
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
      const routePath = `/offres${isNew ? 'nouveau' : `/${occasionId}`}`

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
