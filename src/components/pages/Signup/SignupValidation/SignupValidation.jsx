import PropTypes from 'prop-types'
import React, { PureComponent } from 'react'
import { Redirect } from 'react-router-dom'
import { requestData } from 'redux-saga-data'

import { redirectLoggedUser } from 'components/router/helpers'
import { campaignTracker } from 'tracking/mediaCampaignsTracking'

class SignupValidation extends PureComponent {
  constructor(props) {
    super(props)
    const { currentUser, history, isNewHomepageActive } = props
    redirectLoggedUser(history, currentUser, isNewHomepageActive)
  }

  componentDidMount() {
    campaignTracker.signUpValidation()

    const {
      dispatch,
      match: {
        params: { token },
      },
    } = this.props

    dispatch(this.buildRequestData(token))
  }

  buildRequestData = token => {
    return requestData({
      apiPath: `/validate/user/${token}`,
      method: 'PATCH',
      handleSuccess: this.notifySuccess(),
      handleFail: this.notifyFailure(),
    })
  }

  notifyFailure = () => {
    return (state, action) => {
      const {
        payload: { errors },
      } = action

      const { notifyError } = this.props
      notifyError(errors.global)
    }
  }

  notifySuccess = () => {
    return () => {
      const { notifySuccess } = this.props
      notifySuccess(
        'Votre compte a été créé. Vous pouvez vous connecter avec les identifiants que vous avez choisis.'
      )
    }
  }

  render() {
    return <Redirect to="/connexion" />
  }
}

SignupValidation.defaultProps = {
  currentUser: null,
}

SignupValidation.propTypes = {
  currentUser: PropTypes.shape(),
  dispatch: PropTypes.func.isRequired,
  history: PropTypes.func.isRequired,
  isNewHomepageActive: PropTypes.bool.isRequired,
  match: PropTypes.shape({
    params: PropTypes.shape({
      token: PropTypes.string.isRequired,
    }),
  }).isRequired,
  notifyError: PropTypes.func.isRequired,
  notifySuccess: PropTypes.func.isRequired,
}

export default SignupValidation
