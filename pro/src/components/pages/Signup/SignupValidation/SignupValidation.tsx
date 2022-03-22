import PropTypes from 'prop-types'
import { useEffect } from 'react'
import { useHistory, useParams } from 'react-router'

import * as pcapi from 'repository/pcapi/pcapi'
import { campaignTracker } from 'tracking/mediaCampaignsTracking'

type Params = { token: string }

export type Props = {
  notifyError: (message: string) => void
  notifySuccess: (message: string) => void
}

const SignupValidation = ({ notifyError, notifySuccess }: Props): null => {
  const { token } = useParams<Params>()
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
