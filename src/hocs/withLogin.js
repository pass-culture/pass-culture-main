import Cookies from 'js-cookies'
import React, { Component } from 'react'
import { connect } from 'react-redux'

import Sign from '../components/Sign'
import { closeModal, showModal } from '../reducers/modal'
import { assignData, requestData } from '../reducers/data'

const withLogin = (config = {}) => WrappedComponent => {
  const { isRequired } = config
  class _withLogin extends Component {
    constructor () {
      super ()
      this.state = { hasBackendRequested: false,
        hasDexieRequested: false }
    }
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
            this.setState({ hasDexieRequested: true })
          } else {
            // else ask to the backend
            requestData('GET', 'users/me', { key: 'users' })
          }
        }
      }, 1000)
    }
    componentWillReceiveProps = nextProps => {
      const { assignData, requestData } = this.props
      const { hasBackendRequested, hasDexieRequested } = this.state
      if (nextProps.user && nextProps.user !== this.props.user) {
        nextProps.closeModal()
        return
      } else if (isRequired) {
        if (nextProps.user === false && this.props.user === null) {
          if (hasDexieRequested) {
            requestData('GET', 'users/me', { key: 'users' })
            this.setState({ hasBackendRequested: true })
            return
          } else {
            nextProps.showModal(<Sign />, {
              isCloseButton: false,
              isUnclosable: true
            })
          }
        } else if (nextProps.user === null && this.props.user === false) {
          nextProps.showModal(<Sign />, {
            isCloseButton: false,
            isUnclosable: true
          })
        }
      }
    }
    component
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
