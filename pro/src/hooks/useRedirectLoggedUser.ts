import { useEffect } from 'react'
import { useLocation } from 'react-router'

import { useNavigate } from 'hooks'

import useCurrentUser from './useCurrentUser'

const useRedirectLoggedUser = () => {
  const navigate = useNavigate()
  const location = useLocation()
  const { currentUser } = useCurrentUser()

  useEffect(() => {
    if (currentUser) {
      let redirectUrl = null

      const queryParams = new URLSearchParams(location.search)
      if (queryParams.has('de')) {
        redirectUrl = queryParams.get('de')
      } else if (currentUser.isAdmin) {
        redirectUrl = `/structures${location.search}`
      } else {
        redirectUrl = `/accueil${location.search}`
      }
      redirectUrl && navigate(redirectUrl)
    }
  }, [currentUser])
}

export default useRedirectLoggedUser
