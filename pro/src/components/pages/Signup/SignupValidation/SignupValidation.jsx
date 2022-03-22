import PropTypes from 'prop-types'
import { useEffect } from 'react'
import { useHistory, useParams } from 'react-router'

import * as pcapi from 'repository/pcapi/pcapi'
import { campaignTracker } from 'tracking/mediaCampaignsTracking'

const SignupValidation = ({ notifyError, notifySuccess }) => {
  let { token } = useParams()
  const history = useHistory()
  useEffect(() => {
    campaignTracker.signUpValidation()
  }, [])

  useEffect(() => {
    if (token)
      pcapi
        .validateUser(token)
        .then(() => {
          notifySuccess(
            'Votre compte a été créé. Vous pouvez vous connecter avec les identifiants que vous avez choisis.'
          )
        })
        .catch(payload => {
          const { errors } = payload
          notifyError(errors.global)
        })
        .finally(() => history.push('/connexion'))
  }, [history, notifyError, notifySuccess, token])
  return null
}
SignupValidation.defaultProps = {
  currentUser: null,
}

SignupValidation.propTypes = {
  notifyError: PropTypes.func.isRequired,
  notifySuccess: PropTypes.func.isRequired,
}

export default SignupValidation
