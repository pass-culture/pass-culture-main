import React, { Component } from 'react'
import { connect } from 'react-redux'
import { withRouter } from 'react-router'
import { compose } from 'redux'

import { requestData } from '../../reducers/data'
import createSelectCurrentOccasion from '../../selectors/currentOccasion'
import { NEW } from '../../utils/config'
import { pathToCollection } from '../../utils/translate'
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

    handleRequestData = () => {
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
      this.props.user && this.handleRequestData()
    }

    componentDidUpdate(prevProps) {
      const { user } = this.props
      if (user && user !== prevProps.user) {
        this.handleRequestData()
      }
    }

    static getDerivedStateFromProps (nextProps) {
      const {
        currentOccasion,
        match: { params: { occasionId } },
      } = nextProps
      const {
        id
      } = (currentOccasion || {})
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

  const selectCurrentOccasion = createSelectCurrentOccasion()

  return compose(
    withRouter,
    connect(
      (state, ownProps) => ({
        currentOccasion: selectCurrentOccasion(state, ownProps),
        user: state.user,
      }),
      { requestData }
    )
  )(_withCurrentOccasion)
}

export default withCurrentOccasion
