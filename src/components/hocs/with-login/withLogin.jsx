import PropTypes from 'prop-types'
import React, { PureComponent } from 'react'
import { connect } from 'react-redux'

import LoadingPage from '../../layout/LoadingPage/LoadingPage'
import { getCurrentUser } from '../../../redux/actions/currentUser'

export default (config = {}) => WrappedComponent => {
  const { handleFail, handleSuccess } = config
  const isRequired = typeof config.isRequired === 'undefined' ? true : config.isRequired

  class _withLogin extends PureComponent {
    constructor() {
      super()
      this.state = {
        canRenderChildren: false,
      }
    }

    componentDidMount = async () => {
      const { getCurrentUser } = this.props

      const setCurrentUserAction = await getCurrentUser()

      const currentUser = setCurrentUserAction.value
      if (currentUser) {
        this.handleSuccessLogin(currentUser)
      } else {
        this.handleFailLogin()
      }
    }

    handleFailLogin = () => {
      if (!isRequired) {
        this.setState({ canRenderChildren: true }, () => {
          if (handleFail) {
            handleFail(this.props)
          }
        })
        return
      }

      if (handleFail) {
        handleFail(this.props)
      }
    }

    handleSuccessLogin = currentUser => {
      const canRenderChildren = isRequired ? !!currentUser : true

      this.setState(
        {
          canRenderChildren,
        },
        () => {
          if (handleSuccess) {
            handleSuccess(currentUser, this.props)
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
    getCurrentUser: PropTypes.func.isRequired,
  }

  return connect(
    undefined,
    { getCurrentUser }
  )(_withLogin)
}
