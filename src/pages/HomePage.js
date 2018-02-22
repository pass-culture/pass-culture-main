import React, { Component } from 'react'
import { connect } from 'react-redux'
import { withRouter } from 'react-router'
import { compose } from 'redux'

class HomePage extends Component {
  handleRedirect = props => {
    const { history: { push }, user } = props
    push(user.userOfferers && user.userOfferers ? '/pro' : '/decouverte')
  }
  componentWillMount () {
    this.props.user && this.handleRedirect(this.props)
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
  connect(
    state => ({ user: state.user })
  )
)(HomePage)
