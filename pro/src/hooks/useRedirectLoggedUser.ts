import { useEffect } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'

import { api } from 'apiClient/api'

import useActiveFeature from './useActiveFeature'
import useCurrentUser from './useCurrentUser'

const useRedirectLoggedUser = () => {
  const navigate = useNavigate()
  const location = useLocation()
  const { currentUser } = useCurrentUser()
  const newOnboardingActive = useActiveFeature('WIP_ENABLE_NEW_ONBOARDING')

  const redirecTotUrl = () => {
    const queryParams = new URLSearchParams(location.search)
    const redirectUrl = queryParams.has('de')
      ? queryParams.get('de')
      : `/accueil${location.search}`
    redirectUrl && navigate(redirectUrl)
  }

  useEffect(() => {
    async function fetchOfferersNames() {
      const listOfferer = await api.listOfferersNames()
      if (listOfferer.offerersNames.length === 0) {
        navigate('/parcours-inscription')
      } else {
        redirecTotUrl()
      }
    }

    if (currentUser) {
      if (newOnboardingActive && !currentUser.isAdmin) {
        fetchOfferersNames()
      } else {
        redirecTotUrl()
      }
    }
  }, [currentUser])
}

export default useRedirectLoggedUser
