// POSSIBLE HOC FOR ALL OTHER THE PAGE THAN SIGNIN AND SIGNUP
// withLogin ASK FOR A CONNECTED USER, IF NOT IT REDIRECTS TO SININGPAGE
// ON USER SUCCESS IT CAN ALSO REDIRECT TO A SPECIFIC PATH
import React, { Component } from 'react'
import { connect } from 'react-redux'
import { withRouter } from 'react-router'
import { compose } from 'redux'

import { requestData } from '../../reducers/data'
import { IS_DEXIE } from '../../utils/config'

const withLogin = (config = {}) => WrappedComponent => {
  const { isRequired, redirectTo } = config
  const pushSigninTimeout = config.pushSigninTimeout || 500

  class _withLogin extends Component {
    constructor() {
      super()
      this.hasBackendRequest = false
      this.state = { hasConfirmRequest: false }
    }

    componentWillMount = () => {
      const { user, requestData } = this.props
      if (!user) {
        requestData('GET', `users/me`, {
          key: 'users',
          local: IS_DEXIE
        })
      } else if (redirectTo) {
        this.setState({ redirectTo })
      }
    }

    componentWillReceiveProps = nextProps => {
      const {
        history,
        isModalActive,
        requestData
      } = this.props
      if (nextProps.user && nextProps.user !== this.props.user) {
        // BUT ACTUALLY IT IS A SUCCESS FROM THE LOCAL USER
        // NOW BETTER IS TO ALSO TO DO A QUICK CHECK
        // ON THE BACKEND TO CONFIRM THAT IT IS STILL
        // A STORED USER
        if (!this.props.user && !this.hasBackendRequest) {
          requestData('GET', `users/me`, { key: 'users' })
          this.hasBackendRequest = true
          if (redirectTo) {
            history.push(redirectTo)
          }
        }
      } else if (isRequired) {
        if (nextProps.user === false && this.props.user === null) {
          // CASE WHERE WE TRIED TO GET THE USER IN THE LOCAL
          // BUT WE GOT A FALSE RETURN SO WE NEED TO ASK THE BACKEND
          requestData('GET', 'users/me', { key: 'users' })
          this.hasBackendRequest = true
        } else if (!isModalActive) {
          if (nextProps.user === null && this.props.user === false) {
            // CASE WHERE WE STILL HAVE A USER NULL
            // SO WE FORCE THE SIGNIN PUSH
            history.push('/connexion')
          } else if (nextProps.user === false && this.props.user) {
            // CASE WE JUST SIGNOUT AND AS IT IS REQUIRED IS TRUE
            // WE NEED TO PROPOSE A NEW SIGNIN MODAL
            // BUT WE ARE GOING TO WAIT JUST A LITTLE BIT
            // TO MAKE A SLOW TRANSITION
            this.pushSigninTimeout = setTimeout(
              () => history.push('/connexion'),
              pushSigninTimeout
            )
          }
        }
      }
    }

    componentWillUnmount() {
      this.pushSigninTimeout && clearTimeout(this.pushSigninTimeout)
    }

    render() {
      return <WrappedComponent {...this.props} />
    }
  }
  return compose(
    withRouter,
    connect(
      state => ({ isModalActive: state.modal.isActive, user: state.user }),
      { requestData }
    )
  )(_withLogin)
}

export default withLogin
