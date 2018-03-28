import React, { Component } from 'react'
import { connect } from 'react-redux'

import Sign from '../components/Sign'
import { closeModal, showModal } from '../reducers/modal'
import { requestData } from '../reducers/data'

const withLogin = (config = {}) => WrappedComponent => {
  const { isRequired } = config;

  class _withLogin extends Component {
    componentDidMount() {
      // setTimeout(() => {
        !this.props.user && this.props.requestData('GET', 'users/me', { key: 'users', sync: true })
      // }, 1000)
    }

    componentWillReceiveProps(nextProps) {
      this.handleModalState(nextProps);
    }

    handleModalState(props) {
      // if (props.activeModal && props.user) {
      //   props.closeModal();
      // } else
      if (!props.activeModal && !props.user && isRequired) {
        props.showModal(<Sign />, {
          isCloseButton: false,
          isUnclosable: true
        })
      }
    }

    render() {
      return <WrappedComponent {...this.props} />
    }
  }

  return connect(
    ({ user, modal }) => ({
      user,
      activeModal: modal && modal.isActive
    }),
    {
      closeModal,
      requestData,
      showModal
    }
  )(_withLogin)
}

export default withLogin
