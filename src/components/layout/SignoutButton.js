import React, { Component } from 'react'
import { connect } from 'react-redux'
import { withRouter } from 'react-router-dom'
import { compose } from 'redux'

import { requestData } from '../../reducers/data'
import { closeModal } from '../../reducers/modal'

class SignoutButton extends Component {

  static defaultProps = {
    tagName: 'button',
  }

  onSignoutClick = () => {
    const { closeModal, requestData } = this.props
    requestData('GET', 'users/signout')
    closeModal()
  }

  componentDidUpdate (prevProps) {
    const { history, user } = this.props
    if (!user && prevProps.user) {
      history.push('/connexion')
    }
  }

  render () {
    const TagName = this.props.tagName
    return (
      <TagName onClick={this.onSignoutClick} className={this.props.className}>{this.props.children}</TagName>
    )
  }
}

export default compose(
  withRouter,
  connect(
    state => ({ user: state.user }),
    { closeModal, requestData }
  )
)(SignoutButton)
