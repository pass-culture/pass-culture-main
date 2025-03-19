import { useEffect, useState } from 'react'
import { useSelector } from 'react-redux'
import { useParams, Navigate } from 'react-router-dom'

import { api } from 'apiClient/api'
import { getError, isErrorAPIError } from 'apiClient/helpers'
import { useActiveFeature } from 'commons/hooks/useActiveFeature'
import { selectCurrentUser } from 'commons/store/user/selectors'

type Params = { token: string }

export const SignupValidation = (): JSX.Element | null => {
  const { token } = useParams<Params>()
  const currentUser = useSelector(selectCurrentUser)
  const [urlToRedirect, setUrlToRedirect] = useState<string>()
  const isNewSignupEnabled = useActiveFeature('WIP_2025_SIGN_UP')

  useEffect(() => {
    const validateTokenAndRedirect = async () => {
      if (currentUser?.id) {
        setUrlToRedirect('/')
      } else if (token) {
        try {
          await api.validateUser(token)
          isNewSignupEnabled ? setUrlToRedirect('/accueil') : setUrlToRedirect('/connexion?accountValidation=true')
        } catch (error) {
          if (isErrorAPIError(error)) {
            const errors = getError(error)
            // TODO: if we use notify, the notification doesn't appear,
            // we have to send the message and status with get parameters
            setUrlToRedirect(
              '/connexion?accountValidation=false&message=' + errors.global
            )
          } else {
            setUrlToRedirect('/connexion')
          }
        }
      }
    }
    // eslint-disable-next-line @typescript-eslint/no-floating-promises
    validateTokenAndRedirect()
  }, [token, currentUser?.id])

  return urlToRedirect ? <Navigate to={urlToRedirect} replace /> : null
}
