import { useEffect, useState } from 'react'
import { useSelector , useDispatch } from 'react-redux'
import { useParams, Navigate } from 'react-router-dom'

import { api } from 'apiClient/api'
import { getError, isErrorAPIError } from 'apiClient/helpers'
import { SAVED_OFFERER_ID_KEY } from 'commons/core/shared/constants'
import { useActiveFeature } from 'commons/hooks/useActiveFeature'
import { updateOffererIsOnboarded, updateOffererNames, updateSelectedOffererId } from 'commons/store/offerer/reducer'
import { updateUser } from 'commons/store/user/reducer'
import { selectCurrentUser } from 'commons/store/user/selectors'
import { storageAvailable } from 'commons/utils/storageAvailable'

type Params = { token: string }

export const SignupValidation = (): JSX.Element | null => {
  const { token } = useParams<Params>()
  const currentUser = useSelector(selectCurrentUser)
  const [urlToRedirect, setUrlToRedirect] = useState<string>()
  const isNewSignupEnabled = useActiveFeature('WIP_2025_SIGN_UP')
  const dispatch = useDispatch()

  useEffect(() => {
    const validateTokenAndRedirect = async () => {
      if (currentUser?.id) {
        setUrlToRedirect('/')
      } else if (token) {
        try {
          await api.validateUser(token)
          if (isNewSignupEnabled) {
            // TODO: Make util function with signin
            const inisializeOffererIsOnboarded = async (offererId: number) => {
              const response = await api.getOfferer(offererId)
              dispatch(updateOffererIsOnboarded(response.isOnboarded))
            }

            const offerers = await api.listOfferersNames()
            const firstOffererId = offerers.offerersNames[0]?.id

            if (firstOffererId) {
              dispatch(updateOffererNames(offerers.offerersNames))

              if (storageAvailable('localStorage')) {
                const savedOffererId = localStorage.getItem(SAVED_OFFERER_ID_KEY)
                dispatch(
                  updateSelectedOffererId(
                    savedOffererId ? Number(savedOffererId) : firstOffererId
                  )
                )
                await inisializeOffererIsOnboarded(
                  savedOffererId ? Number(savedOffererId) : firstOffererId
                )
              } else {
                dispatch(updateSelectedOffererId(firstOffererId))
                await inisializeOffererIsOnboarded(firstOffererId)
              }
            }

            const user = await api.getProfile()
            dispatch(updateUser(user))
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
  }, [token, currentUser?.id])

  return urlToRedirect ? <Navigate to={urlToRedirect} replace /> : null
}
