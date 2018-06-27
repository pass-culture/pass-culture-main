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

    constructor(props) {
      super(props)
      this.isRequired = isRequired || Boolean(props.handleDataRequest)
      this.redirectTo = redirectTo
    }

    componentWillMount = () => {
      const { user, requestData } = this.props
      if (this.isRequired && !user) {
        requestData('GET', `users/me`, { key: 'users' })
      }
    }

    componentDidMount = () => {
      this.handleRedirect()
    }

    componentDidUpdate = prevProps => {
      this.handleRedirect(prevProps)
    }

    handleRedirect = (prevProps={}) => {
      const { history, location, user } = this.props
      if (user && user !== prevProps.user) {
        if (!prevProps.user && this.redirectTo && this.redirectTo !== location.pathname) {
          history.push(this.redirectTo)
        }
      } else if (this.isRequired) {
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
