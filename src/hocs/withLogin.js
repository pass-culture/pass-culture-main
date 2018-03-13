import Cookies from 'js-cookies'
import React, { Component } from 'react'
import { connect } from 'react-redux'

import Sign from '../components/Sign'
import { closeModal, showModal } from '../reducers/modal'
import { requestData } from '../reducers/data'

const withLogin = (config = {}) => WrappedComponent => {
  const { isRequired } = config
  class _withLogin extends Component {
    componentWillMount = () => {
      // be sure that user is not defined yet by waiting a bit
      setTimeout(() => {
        const { user, requestData } = this.props
        if (!user) {
          // ask to dexie if we don't have the user in storage
          const rememberToken = Cookies.getItem('remember_token')
          if (rememberToken) {
            requestData('GET', `users/me?rememberToken=${rememberToken}`,
              { key: 'users', sync: true })
          }
        }
        // !user && requestData('GET', 'users/me', { key: 'users' })
      }, 1000)
    }
    componentWillReceiveProps = nextProps => {
      if (nextProps.user && nextProps.user !== this.props.user) {
        nextProps.closeModal()
      } else if (isRequired && !nextProps.user) {
        nextProps.showModal(<Sign />, {
          isCloseButton: false,
          isUnclosable: true
        })
      }
    }
    render () {
      return <WrappedComponent {...this.props} />
    }
  }
  return connect(
    ({ user }) => ({ user }),
    { closeModal, requestData, showModal }
  )(_withLogin)
}

export default withLogin
