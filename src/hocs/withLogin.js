import React, { Component } from 'react'
import { connect } from 'react-redux'

import Sign from '../components/Sign'
import { closeModal, showModal } from '../reducers/modal'
import { requestData } from '../reducers/data'

const withLogin = WrappedComponent => {
  class _withLogin extends Component {
    componentWillMount = () => {
      // be sure that user is not defined yet by waiting a bit
      setTimeout(() => {
        const { user, requestData } = this.props
        !user && requestData('GET', 'users/me', { key: 'users' })
      }, 1000)
    }
    componentWillReceiveProps = nextProps => {
      if (nextProps.user && nextProps.user !== this.props.user) {
        nextProps.closeModal()
      } else if (!nextProps.user) {
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
