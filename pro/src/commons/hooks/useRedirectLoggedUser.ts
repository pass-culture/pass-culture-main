import { useEffect } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { useNavigate, useSearchParams } from 'react-router-dom'

import { api } from 'apiClient/api'
import { SAVED_OFFERER_ID_KEY } from 'commons/core/shared/constants'
import { updateSelectedOffererId } from 'commons/store/offerer/reducer'
import { updateUser } from 'commons/store/user/reducer'
import { selectCurrentUser } from 'commons/store/user/selectors'
import { storageAvailable } from 'commons/utils/storageAvailable'
import { SAVED_VENUE_ID_KEY } from 'pages/Homepage/components/Offerers/components/PartnerPages/PartnerPages'

export const useRedirectLoggedUser = () => {
  const navigate = useNavigate()
  const currentUser = useSelector(selectCurrentUser)
  const dispatch = useDispatch()

  const [searchParams] = useSearchParams()
  const redirectToUrl = () => {
    const redirectUrl = searchParams.has('de')
      ? searchParams.get('de')
      : `/accueil?${searchParams}`
    if (redirectUrl) {
      navigate(redirectUrl)
    }
  }

  useEffect(() => {
    async function fetchOfferersNames() {
      const { offerersNames } = await api.listOfferersNames()
      if (offerersNames.length === 0) {
        navigate('/parcours-inscription')
      } else {
        redirectToUrl()
      }
    }

    if (currentUser) {
      // eslint-disable-next-line @typescript-eslint/no-floating-promises
      fetchOfferersNames()
    } else {
      // Reset the user and selected offerer to prevent issues when connecting
      if (storageAvailable('localStorage')) {
        localStorage.removeItem(SAVED_OFFERER_ID_KEY)
        localStorage.removeItem(SAVED_VENUE_ID_KEY)
      }
      dispatch(updateUser(null))
      dispatch(updateSelectedOffererId(null))
    }
  }, [currentUser])
}
