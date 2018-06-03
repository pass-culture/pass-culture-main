import React, { Component } from 'react'
import { connect } from 'react-redux'
import { withRouter } from 'react-router'
import { compose } from 'redux'

import { requestData } from '../../reducers/data'
import selectCurrentOccasion from '../../selectors/currentOccasion'
import { pathToCollection } from '../../utils/translate'

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
        { key: 'occasions' }
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
        occasionId,
        occasionPath
      } = nextProps.match.params
      const {
        id
      } = nextProps
      const isNew = nextProps.match.params.occasionId === 'nouveau'
      const apiPath = `occasions/${pathToCollection(occasionPath)}/${occasionId}`
      const routePath = `/offres/${occasionPath}/${occasionId !== 'nouveau' ? occasionId : ''}`
      return {
        apiPath,
        isLoading: !(id || isNew),
        isNew,
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
      (state, ownProps) =>
        Object.assign(
          { user: state.user },
          selectCurrentOccasion(state, ownProps)
        ),
      { requestData }
    )
  )(_withCurrentOccasion)
}

export default withCurrentOccasion
