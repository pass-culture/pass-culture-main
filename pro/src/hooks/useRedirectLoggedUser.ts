import { useEffect } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'

import { api } from 'apiClient/api'

import useCurrentUser from './useCurrentUser'

const useRedirectLoggedUser = () => {
  const navigate = useNavigate()
  const { currentUser } = useCurrentUser()

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
      if (!currentUser.isAdmin) {
        fetchOfferersNames()
      } else {
        redirectToUrl()
      }
    }
  }, [currentUser])
}

export default useRedirectLoggedUser
