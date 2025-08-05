import { api } from 'apiClient/api'
import { getError, isErrorAPIError } from 'apiClient/helpers'
import { useActiveFeature } from 'commons/hooks/useActiveFeature'
import { AppDispatch } from 'commons/store/store'
import { selectCurrentUser } from 'commons/store/user/selectors'
import { initializeUserThunk } from 'commons/store/user/thunks'
import { useEffect, useRef, useState } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { Navigate, useParams } from 'react-router'

type Params = { token: string }

export const SignupValidation = (): JSX.Element | null => {
  const { token } = useParams<Params>()
  const currentUser = useSelector(selectCurrentUser)
  const [urlToRedirect, setUrlToRedirect] = useState<string>()
  const isAutologinEnabled = useActiveFeature('WIP_2025_AUTOLOGIN')
  const dispatch = useDispatch<AppDispatch>()

  const tokenConsumed = useRef(false)

  useEffect(() => {
    const validateTokenAndRedirect = async () => {
      if (currentUser?.id) {
        setUrlToRedirect('/')
      } else if (token && !tokenConsumed.current) {
        try {
          // Ensure that we call only 1 time the API upon different re-renders
          tokenConsumed.current = true
          await api.validateUser(token)
          if (isAutologinEnabled) {
            const user = await api.getProfile()
            const result = await dispatch(initializeUserThunk(user)).unwrap()
            if (result.success) {
              setUrlToRedirect('/')
            }
          } else {
            setUrlToRedirect('/connexion?accountValidation=true')
          }
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
  }, [token, currentUser?.id, isAutologinEnabled, dispatch])

  return urlToRedirect ? <Navigate to={urlToRedirect} replace /> : null
}
