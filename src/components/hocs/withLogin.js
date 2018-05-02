// POSSIBLE HOC FOR ALL OTHER THE PAGE THAN SIGNIN AND SIGNUP
// withLogin ASK FOR A CONNECTED USER, IF NOT IT REDIRECTS TO SIGNING PAGE
// ON USER SUCCESS IT CAN ALSO REDIRECT TO A SPECIFIC PATH
import React, { Component } from 'react'
import { connect } from 'react-redux'
import { withRouter } from 'react-router'
import { compose } from 'redux'

import { requestData } from '../../reducers/data'

const withLogin = (config = {}) => WrappedComponent => {
  const { isRequired, redirectTo } = config

  class _withLogin extends Component {
    componentWillMount = () => {
      const { user, requestData } = this.props
      if (!user) {
        requestData('GET', `users/me`, { key: 'users' })
      }
    }

    componentDidUpdate = prevProps => {
      const { history, user } = this.props
      if (user && user !== prevProps.user) {
        if (!prevProps.user && redirectTo) {
          history.push(redirectTo)
        }
      } else if (isRequired) {
        if (user === false && prevProps.user === null) {
          // CASE WHERE WE STILL HAVE A USER NULL
          // SO WE FORCE THE SIGNING PUSH
          history.push('/connexion')
        }
      }
    }

    render() {
      return <WrappedComponent {...this.props} />
    }
  }
  return compose(
    withRouter,
    connect(
      state => ({ user: state.user }),
      { requestData }
    )
  )(_withLogin)
}

export default withLogin
