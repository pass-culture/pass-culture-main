import classnames from 'classnames'
import React, { Component } from 'react'
import { connect } from 'react-redux'
import { NavLink, withRouter } from 'react-router-dom'
import { compose } from 'redux'

import Icon from './Icon'
import { requestData } from '../../reducers/data'
import { closeModal } from '../../reducers/modal'

class SigninOut extends Component {

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
    const { className,
      signinElement,
      signoutElement,
      user
    } = this.props
    return (
      <NavLink className={classnames('signin-out', className)}
        to={window.location.pathname}>
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

export default compose(
  withRouter,
  connect(
    state => ({ user: state.user }),
    { closeModal, requestData }
  )
)(SigninOut)
