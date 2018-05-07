import React, { Component } from 'react'
import { connect } from 'react-redux'

import Icon from './Icon'
import { requestData } from '../../reducers/data'
import { closeModal } from '../../reducers/modal'

class SigninOut extends Component {

  onSignOutClick = () => {
    const { closeModal, requestData } = this.props
    requestData('GET', 'users/signout')
    closeModal()
  }

  render () {
    const { className, children } = this.props
    return (
      <div className={className} onClick={this.onSignOutClick}>
        {children}
      </div>
    )
  }
}

export default connect(
  state => ({ user: state.user }),
  { closeModal, requestData }
)(SigninOut)
