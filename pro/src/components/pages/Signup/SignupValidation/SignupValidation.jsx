import PropTypes from 'prop-types'
import React, { PureComponent } from 'react'
import { Redirect } from 'react-router-dom'

import { redirectLoggedUser } from 'components/router/helpers'
import * as pcapi from 'repository/pcapi/pcapi'
import { campaignTracker } from 'tracking/mediaCampaignsTracking'

/**
 * @debt standard "Annaëlle: Composant de classe à migrer en fonctionnel"
 */
class SignupValidation extends PureComponent {
  constructor(props) {
    super(props)
    const { currentUser, location, history } = props
    redirectLoggedUser(history, location, currentUser)
  }

  componentDidMount() {
    campaignTracker.signUpValidation()

    const {
      match: {
        params: { token },
      },
    } = this.props

    this.buildRequestData(token)
  }

  buildRequestData = async token => {
    await pcapi
      .validateUser(token)
      .then(() => this.notifySuccess())
      .catch(payload => this.notifyFailure(payload))
  }

  notifyFailure = payload => {
    const { errors } = payload
    const { notifyError } = this.props
    notifyError(errors.global)
  }

  notifySuccess = () => {
    const { notifySuccess } = this.props
    notifySuccess(
      'Votre compte a été créé. Vous pouvez vous connecter avec les identifiants que vous avez choisis.'
    )
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
  history: PropTypes.func.isRequired,
  location: PropTypes.shape().isRequired,
  match: PropTypes.shape({
    params: PropTypes.shape({
      token: PropTypes.string.isRequired,
    }),
  }).isRequired,
  notifyError: PropTypes.func.isRequired,
  notifySuccess: PropTypes.func.isRequired,
}

export default SignupValidation
