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

    componentDidMount = () => {
      const {
        history,
        location,
        user,
        requestData
      } = this.props

      if (user === null && this.isRequired) {
        requestData('GET', `users/current`, {
          key: 'users',
          handleSuccess: () => {
            if (this.redirectTo && this.redirectTo !== location.pathname)
              history.push(this.redirectTo)
          },
          handleFail: () => {
            history.push('/connexion')
          }
        })
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
