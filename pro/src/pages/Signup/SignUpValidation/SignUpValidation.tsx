import { useEffect } from 'react'
import { useNavigate, useParams } from 'react-router-dom-v5-compat'

import { api } from 'apiClient/api'
import { getError, isErrorAPIError } from 'apiClient/helpers'
import useCurrentUser from 'hooks/useCurrentUser'
import useNotification from 'hooks/useNotification'
import { campaignTracker } from 'tracking/mediaCampaignsTracking'

type Params = { token: string }

const SignupValidation = (): null => {
  const { token } = useParams<Params>()
  const { currentUser } = useCurrentUser()
  const navigate = useNavigate()
  useEffect(() => {
    campaignTracker.signUpValidation()
  }, [])
  const notify = useNotification()
  useEffect(() => {
    if (currentUser?.id) {
      navigate('/')
    } else if (token) {
      api
        .validateUser(token)
        .then(() => {
          notify.success(
            'Votre compte a été créé. Vous pouvez vous connecter avec les identifiants que vous avez choisis.'
          )
        })
        .catch(payload => {
          if (isErrorAPIError(payload)) {
            const errors = getError(payload)
            notify.error(errors.global)
          }
        })
        .finally(() => navigate('/connexion'))
    }
  }, [history, notify, token, currentUser?.id])
  return null
}
SignupValidation.defaultProps = {
  currentUser: null,
}

export default SignupValidation
