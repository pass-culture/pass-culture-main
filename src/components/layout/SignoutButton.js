import get from 'lodash.get'
import { closeModal, requestData } from 'pass-culture-shared'
import React, { Component } from 'react'
import { connect } from 'react-redux'
import { withRouter } from 'react-router-dom'
import { compose } from 'redux'

class SignoutButton extends Component {
  static defaultProps = {
    Tag: 'button',
  }

  handleSignoutError = () => {
    const { error, history } = this.props
    if (error) {
      history.push('/connexion')
    }
  }

  onSignoutClick = () => {
    const { closeModal, requestData } = this.props
    requestData('GET', 'users/signout', { name: 'signout' })
    closeModal()
  }

  componentDidUpdate(prevProps) {
    const { error, history, user } = this.props
    if (!user && prevProps.user) {
      history.push('/connexion')
    }
    if (error !== prevProps.error) {
      this.handleSignoutError()
    }
  }

  render() {
    const { children, className, Tag } = this.props
    return (
      <Tag onClick={this.onSignoutClick} className={className}>
        {children}
      </Tag>
    )
  }
}

export default compose(
  withRouter,
  connect(
    state => ({
      error: get(state.errors, 'signout.global'),
      user: state.user,
    }),
    { closeModal, requestData }
  )
)(SignoutButton)
