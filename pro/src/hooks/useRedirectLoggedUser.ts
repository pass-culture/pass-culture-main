import { useEffect } from 'react'
import { useSelector } from 'react-redux'
import { useNavigate, useSearchParams } from 'react-router-dom'

import { api } from 'apiClient/api'
import { selectCurrentUser } from 'store/user/selectors'

export const useRedirectLoggedUser = () => {
  const navigate = useNavigate()
  const currentUser = useSelector(selectCurrentUser)

  const [searchParams] = useSearchParams()
  const redirectToUrl = () => {
    const redirectUrl = searchParams.has('de')
      ? searchParams.get('de')
      : `/accueil?${searchParams}`
    redirectUrl && navigate(redirectUrl)
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
      if (!currentUser.isAdmin) {
        // eslint-disable-next-line @typescript-eslint/no-floating-promises
        fetchOfferersNames()
      } else {
        redirectToUrl()
      }
    }
  }, [currentUser])
}
