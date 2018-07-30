import { closeModal, requestData } from 'pass-culture-shared'
import React, { Component } from 'react'
import { connect } from 'react-redux'
import { withRouter } from 'react-router-dom'
import { compose } from 'redux'

class SignoutButton extends Component {
  static defaultProps = {
    Tag: 'button',
  }

  onSignoutClick = () => {
    const { closeModal, requestData } = this.props
    requestData('GET', 'users/signout')
    closeModal()
  }

  componentDidUpdate(prevProps) {
    const { history, user } = this.props
    if (!user && prevProps.user) {
      history.push('/connexion')
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
  connect(state => ({ user: state.user }), { closeModal, requestData })
)(SignoutButton)
