import React, { Component } from 'react'
import { connect } from 'react-redux'

import Sign from '../components/Sign'
import { closeModal, showModal } from '../reducers/modal'
import { requestData } from '../reducers/data'

const withLogin = (config = {}) => WrappedComponent => {
  const { isRequired } = config
  const showSignModalTimeout = config.showSignModalTimeout || 500

  class _withLogin extends Component {

    componentWillMount = () => {
      const { user, requestData } = this.props
      !user && requestData('GET', `users/me`, { key: 'users', sync: true })
    }

    componentWillReceiveProps = nextProps => {
      const { isModalActive, requestData } = this.props
      if (nextProps.user && nextProps.user !== this.props.user) {
        // CASE OF LOGIN SUCCESS
        nextProps.closeModal()
        // BUT ACTUALLY IT IS A SUCCESS FROM THE LOCAL USER
        // NOW BETTER IS TO ALSO TO DO A QUICK CHECK
        // ON THE BACKEND TO CONFIRM THAT IT IS STILL
        // A STORED USER
        if (!this.props.user) {
          requestData('GET', `users/me`, { key: 'users' })
        }
        this.setState({ hasConfirmRequest: true })
      } else if (isRequired) {
        if (nextProps.user === false && this.props.user === null) {
          // CASE WHERE WE TRIED TO GET THE USER IN THE LOCAL
          // BUT WE GOT A FALSE RETURN SO WE NEED TO ASK THE BACKEND
          requestData('GET', 'users/me', { key: 'users' })
        } else if (!isModalActive) {
          if (nextProps.user === null && this.props.user === false) {
            // CASE WHERE WE STILL HAVE A USER NULL
            // SO WE FORCE THE SIGN MODAL
            nextProps.showModal(<Sign />, {
              isUnclosable: isRequired
            })
          } else if (nextProps.user === false && this.props.user) {
            // CASE WE JUST SIGNOUT AND AS IS REQUIRED IS TRUE
            // WE NEED TO PROPOSE A NEW SIGNIN MODAL
            // BUT WE ARE GOING TO WAIT JUST A LITTLE BIT
            // TO MAKE A SLOW TRANSITION
            this.showSignModalTimeout = setTimeout(() =>
              nextProps.showModal(<Sign />, {
                isUnclosable: isRequired
              }), showSignModalTimeout)
          }
        }
      }
    }

    componentWillUnmount () {
      this.requestUserMeTimeout && clearTimeout(this.requestUserMeTimeout)
      this.showSignModalTimeout && clearTimeout(this.showSignModalTimeout)
    }

    render () {
      return <WrappedComponent {...this.props} />
    }

  }
  return connect(
    state => ({
      isModalActive: state.modal.isActive,
      user: state.user
    }),
    { closeModal, requestData, showModal }
  )(_withLogin)
}

export default withLogin
