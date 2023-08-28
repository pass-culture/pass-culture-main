import { useEffect, useState } from 'react'
import { useParams, Navigate } from 'react-router-dom'

import { api } from 'apiClient/api'
import { getError, isErrorAPIError } from 'apiClient/helpers'
import useCurrentUser from 'hooks/useCurrentUser'

type Params = { token: string }

const SignupValidation = (): JSX.Element | null => {
  const { token } = useParams<Params>()
  const { currentUser } = useCurrentUser()
  const [urlToRedirect, setUrlToRedirect] = useState<string>()

  useEffect(() => {
    const validateTokenAndRedirect = async () => {
      if (currentUser?.id) {
        setUrlToRedirect('/')
      } else if (token) {
        try {
          await api.validateUser(token)
          setUrlToRedirect('/connexion?accountValidation=true')
        } catch (error) {
          if (isErrorAPIError(error)) {
            const errors = getError(error)
            // FIXME: if we use notify, the notification doesn't appear,
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
    void validateTokenAndRedirect()
  }, [token, currentUser?.id])

  return urlToRedirect ? <Navigate to={urlToRedirect} replace /> : null
}

export default SignupValidation
