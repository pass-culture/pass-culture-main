import React, { Component } from 'react'
import { connect } from 'react-redux'

import Sign from '../components/Sign'
import { closeModal, showModal } from '../reducers/modal'
import { assignData, requestData } from '../reducers/data'

const withLogin = (config = {}) => WrappedComponent => {
  const { isRequired } = config
  class _withLogin extends Component {
    componentWillMount = () => {
      // be sure that user is not defined yet by waiting a bit
      setTimeout(() => {
        const { user, requestData } = this.props
        !user && requestData('GET', `users/me`, { key: 'users', sync: true })
      }, 1000)
    }
    componentWillReceiveProps = nextProps => {
      const { requestData } = this.props
      if (nextProps.user && nextProps.user !== this.props.user) {
        nextProps.closeModal()
        return
      } else if (isRequired) {
        if (nextProps.user === false && this.props.user === null) {
          requestData('GET', 'users/me', { key: 'users' })
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
