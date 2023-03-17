import React from 'react'
import { Navigate, useLocation } from 'react-router-dom'

import useCurrentUser from 'hooks/useCurrentUser'

interface Props {
  children: JSX.Element
}

const ProtectedRoute = ({ children }: Props) => {
  const { currentUser } = useCurrentUser()
  const location = useLocation()
  const fromUrl = encodeURIComponent(`${location.pathname}${location.search}`)

  if (currentUser === null) {
    const loginUrl = fromUrl.includes('logout')
      ? '/connexion'
      : `/connexion?de=${fromUrl}`

    return <Navigate to={loginUrl} replace />
  }

  return children
}

export default ProtectedRoute
