import React, { Component } from 'react'
import { connect } from 'react-redux'
import { NavLink } from 'react-router-dom'

import Icon from './Icon'
import { requestData } from '../../reducers/data'
import { closeModal } from '../../reducers/modal'

class SigninOut extends Component {

  onSignoutClick = () => {
    const { closeModal, requestData } = this.props
    requestData('GET', 'users/signout')
    closeModal()
  }

  render () {
    const { className,
      signinElement,
      signoutElement,
      user
    } = this.props
    return (
      <NavLink className={className} to='/connexion'>
        {
          user
          ? (
            <span onClick={this.onSignoutClick}>
              {signoutElement}
            </span>
          )
          : signinElement
        }
      </NavLink>
    )
  }
}

export default connect(
  state => ({ user: state.user }),
  { closeModal, requestData }
)(SigninOut)
