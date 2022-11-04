import { useEffect } from 'react'
import { useHistory, useLocation } from 'react-router'

import useCurrentUser from './useCurrentUser'

const useRedirectLoggedUser = () => {
  const history = useHistory()
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
      redirectUrl && history.push(redirectUrl)
    }
  }, [currentUser])
}

export default useRedirectLoggedUser
