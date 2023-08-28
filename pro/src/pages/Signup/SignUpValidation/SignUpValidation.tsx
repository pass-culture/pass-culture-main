import { useEffect } from 'react'
import { useNavigate, useParams, Navigate } from 'react-router-dom'

import { api } from 'apiClient/api'
import { getError, isErrorAPIError } from 'apiClient/helpers'
import useCurrentUser from 'hooks/useCurrentUser'
import useNotification from 'hooks/useNotification'

type Params = { token: string }

const SignupValidation = (): JSX.Element => {
  const { token } = useParams<Params>()
  const { currentUser } = useCurrentUser()
  const navigate = useNavigate()
  const notify = useNotification()

  useEffect(() => {
    const validateTokenAndRedirect = async () => {
      if (currentUser?.id) {
        navigate('/')
      } else if (token) {
        try {
          await api.validateUser(token)
          notify.success(
            'Votre compte a été créé. Vous pouvez vous connecter avec les identifiants que vous avez choisis.'
          )
        } catch (error) {
          if (isErrorAPIError(error)) {
            const errors = getError(error)
            notify.error(errors.global)
          }
        }
      }
    }
    void validateTokenAndRedirect()
  }, [notify, token, currentUser?.id])

  return <Navigate to="/connexion" replace />
}

export default SignupValidation
