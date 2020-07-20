import { requestData } from 'redux-thunk-data'

import PropTypes from 'prop-types'
import React, { PureComponent } from 'react'
import LoadingPage from '../../layout/LoadingPage/LoadingPage'

import { connect } from 'react-redux'

export const resolveCurrentUser = userFromRequest => {
  if (!userFromRequest) {
    return null
  }
  return userFromRequest
}

export default (config = {}) => WrappedComponent => {
  const { handleFail, handleSuccess } = config
  const isRequired = typeof config.isRequired === 'undefined' ? true : config.isRequired
  const currentUserApiPath = '/users/current'

  class _withLogin extends PureComponent {
    constructor() {
      super()
      this.state = {
        canRenderChildren: false,
      }
    }

    componentDidMount = () => {
      const { dispatch } = this.props

      dispatch(
        requestData({
          apiPath: currentUserApiPath,
          resolve: resolveCurrentUser,
          ...config,
          handleFail: this.handleFailLogin,
          handleSuccess: this.handleSuccessLogin,
        })
      )
    }

    handleFailLogin = (state, action) => {
      if (!isRequired) {
        this.setState({ canRenderChildren: true }, () => {
          if (handleFail) {
            handleFail(state, action, this.props)
          }
        })
        return
      }

      if (handleFail) {
        handleFail(state, action, this.props)
      }
    }

    handleSuccessLogin = (state, action) => {
      const {
        payload: { datum },
      } = action

      const currentUser = resolveCurrentUser(datum)
      const canRenderChildren = isRequired ? !!currentUser : true

      this.setState(
        {
          canRenderChildren,
        },
        () => {
          if (handleSuccess) {
            handleSuccess(state, action, this.props)
          }
        }
      )
    }

    render() {
      const { canRenderChildren } = this.state

      if (!canRenderChildren) {
        return <LoadingPage />
      }

      return <WrappedComponent {...this.props} />
    }
  }

  _withLogin.propTypes = {
    dispatch: PropTypes.func.isRequired,
  }

  return connect()(_withLogin)
}
