import { useEffect } from 'react'
import { useHistory, useParams } from 'react-router'

import useNotification from 'components/hooks/useNotification'
import * as pcapi from 'repository/pcapi/pcapi'
import { campaignTracker } from 'tracking/mediaCampaignsTracking'

type Params = { token: string }

const SignupValidation = (): null => {
  const { token } = useParams<Params>()
  const history = useHistory()
  useEffect(() => {
    campaignTracker.signUpValidation()
  }, [])
  const notify = useNotification()
  useEffect(() => {
    if (token)
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
  }, [history, notify, token])
  return null
}
SignupValidation.defaultProps = {
  currentUser: null,
}

export default SignupValidation
