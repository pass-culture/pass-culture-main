import React, { Component } from 'react'
import { connect } from 'react-redux'

import Sign from '../components/Sign'
import { closeModal, showModal } from '../reducers/modal'
import { requestData } from '../reducers/data'

const withLogin = (config = {}) => WrappedComponent => {
  const { isRequired } = config
  const requestUserMeTimeout = config.requestUserMeTimeout || 1000
  const showSignModalTimeout = config.showSignModalTimeout || 500

  class _withLogin extends Component {

    componentWillMount = () => {
      // be sure that user is not defined yet by waiting a bit
      this.requestUserMeTimeout = setTimeout(() => {
        const { user, requestData } = this.props
        !user && requestData('GET', `users/me`, { key: 'users', sync: true })
      }, requestUserMeTimeout)
    }

    componentWillReceiveProps = nextProps => {
      const { requestData } = this.props

      console.log('HEIII', nextProps.user, this.props.user)


      if (nextProps.user && nextProps.user !== this.props.user) {
        // CASE OF LOGIN SUCCESS
        nextProps.closeModal()
      } else if (isRequired) {
        if (nextProps.user === false && this.props.user === null) {
          // CASE WHERE WE TRIED TO GET THE USER IN THE LOCAL
          // BUT WE GOT A FALSE RETURN SO WE NEED TO ASK THE BACKEND
          requestData('GET', 'users/me', { key: 'users' })
        } else if (nextProps.user === null && this.props.user === false) {
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

    componentWillUnmount () {
      this.requestUserMeTimeout && clearTimeout(this.requestUserMeTimeout)
      this.showSignModalTimeout && clearTimeout(this.showSignModalTimeout)
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
