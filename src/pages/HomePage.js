import React, { Component } from 'react'
import { compose } from 'redux'
import { connect } from 'react-redux'
import { withRouter } from 'react-router'

import withLogin from '../hocs/withLogin'

class HomePage extends Component {
  handleRedirect = props => {
    const { history: { push }, user } = props
    user && push(user.isPro ? '/pro' : '/decouverte')
  }
  componentWillMount () {
    this.handleRedirect(this.props)
  }
  componentWillReceiveProps (nextProps) {
    if (nextProps.user !== this.props.user) {
      this.handleRedirect(nextProps)
    }
  }
  render () {
    return (
      <main className='page home-page' />
    )
  }
}

export default compose(
  withRouter,
  withLogin({ isRequired: true }),
  connect(
    state => ({ user: state.user })
  )
)(HomePage)
