import * as pcapi from 'repository/pcapi/pcapi'

import { useHistory, useParams } from 'react-router-dom'

import { campaignTracker } from 'tracking/mediaCampaignsTracking'
import useCurrentUser from 'components/hooks/useCurrentUser'
import { useEffect } from 'react'
import useNotification from 'components/hooks/useNotification'

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
      pcapi
        .validateUser(token)
        .then(() => {
          notify.success(
            'Votre compte a été créé. Vous pouvez vous connecter avec les identifiants que vous avez choisis.'
          )
        })
        .catch(payload => {
          const { errors } = payload
          notify.error(errors.global)
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
