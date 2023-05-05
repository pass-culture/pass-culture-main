import { useEffect } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'

import { api } from 'apiClient/api'

import useActiveFeature from './useActiveFeature'
import useCurrentUser from './useCurrentUser'

const useRedirectLoggedUser = () => {
  const navigate = useNavigate()
  const { currentUser } = useCurrentUser()
  const newOnboardingActive = useActiveFeature('WIP_ENABLE_NEW_ONBOARDING')

  const [searchParams] = useSearchParams()
  const redirectToUrl = () => {
    const redirectUrl = searchParams.has('de')
      ? searchParams.get('de')
      : `/accueil?${searchParams}`
    redirectUrl && navigate(redirectUrl)
  }

  useEffect(() => {
    async function fetchOfferersNames() {
      const listOfferer = await api.listOfferersNames()
      if (listOfferer.offerersNames.length === 0) {
        navigate('/parcours-inscription')
      } else {
        redirectToUrl()
      }
    }

    if (currentUser) {
      if (newOnboardingActive && !currentUser.isAdmin) {
        fetchOfferersNames()
      } else {
        redirectToUrl()
      }
    }
  }, [currentUser])
}

export default useRedirectLoggedUser
