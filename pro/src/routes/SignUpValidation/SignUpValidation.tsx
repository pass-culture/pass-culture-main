import { useEffect } from 'react'
import { useHistory, useParams } from 'react-router-dom'

import { api } from 'apiClient/api'
import { getError, isErrorAPIError } from 'apiClient/helpers'
import useCurrentUser from 'components/hooks/useCurrentUser'
import useNotification from 'components/hooks/useNotification'
import { campaignTracker } from 'tracking/mediaCampaignsTracking'

type Params = { token: string }

const SignupValidation = (): null => {
  const { token } = useParams<Params>()
  const { currentUser } = useCurrentUser()
  const history = useHistory()
  useEffect(() => {
    campaignTracker.signUpValidation()
  }, [])
  const notify = useNotification()
  useEffect(() => {
    if (currentUser?.id) {
      history.push('/')
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
        .finally(() => history.push('/connexion'))
    }
  }, [history, notify, token, currentUser?.id])
  return null
}
SignupValidation.defaultProps = {
  currentUser: null,
}

export default SignupValidation
