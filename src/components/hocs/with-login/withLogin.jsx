import { requestData } from 'redux-thunk-data'

import PropTypes from 'prop-types'
import React, { PureComponent } from 'react'
import LoadingPage from '../../layout/LoadingPage/LoadingPage'

import { connect } from 'react-redux'
import { selectCurrentUser, resolveCurrentUser } from '../../../selectors/data/usersSelectors'

export default (config = {}) => WrappedComponent => {
  const { handleFail, handleSuccess } = config
  const isRequired = typeof config.isRequired === 'undefined' ? true : config.isRequired
  const currentUserApiPath = '/users/current'

  class _withLogin extends PureComponent {
    constructor(props) {
      super(props)
      const { initialCurrentUser } = props
      this.state = {
        canRenderChildren: false,
        currentUser: initialCurrentUser,
      }
    }

    componentDidMount = () => {
      const { dispatch } = this.props

      dispatch(
        requestData(
          Object.assign(
            {
              apiPath: currentUserApiPath,
              resolve: resolveCurrentUser,
              ...config,
            },
            {
              handleFail: this.handleFailLogin,
              handleSuccess: this.handleSuccessLogin,
            }
          )
        )
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

      this.setState(
        {
          canRenderChildren: true,
          currentUser: resolveCurrentUser(datum),
        },
        () => {
          if (handleSuccess) {
            handleSuccess(state, action, this.props)
          }
        }
      )
    }

    render() {
      const { canRenderChildren, currentUser } = this.state

      if (!canRenderChildren || (isRequired && !currentUser)) {
        return <LoadingPage />
      }

      return (<WrappedComponent
        {...this.props}
        currentUser={currentUser}
              />)
    }
  }

  _withLogin.defaultProps = {
    initialCurrentUser: null,
  }

  _withLogin.propTypes = {
    dispatch: PropTypes.func.isRequired,
    initialCurrentUser: PropTypes.shape(),
  }

  return connect(state => ({
    currentUser: selectCurrentUser(state),
  }))(_withLogin)
}
