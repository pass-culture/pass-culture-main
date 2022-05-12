import React from 'react'

import useCurrentUser from 'components/hooks/useCurrentUser'

const useHomePath = () => {
  const {
    currentUser: { isAdmin },
  } = useCurrentUser()
  return isAdmin ? '/structures' : '/accueil'
}

export default useHomePath
