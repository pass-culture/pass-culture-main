import React, { ComponentType, ReactNode } from 'react'
import { Navigate, useLocation } from 'react-router-dom'

import { RouteConfig } from 'app/AppRouter/routesMap'
import useCurrentUser from 'hooks/useCurrentUser'

interface RouteWrapperProps {
  children: React.ReactNode
  routeMeta: RouteConfig['meta']
}

export const RouteWrapper = ({ children, routeMeta }: RouteWrapperProps) => {
  const { currentUser } = useCurrentUser()
  const location = useLocation()
  const fromUrl = encodeURIComponent(`${location.pathname}${location.search}`)
  let jsx: ReactNode = children

  if (!routeMeta?.public && currentUser === null) {
    const loginUrl = fromUrl.includes('logout')
      ? '/connexion'
      : `/connexion?de=${fromUrl}`

    jsx = <Navigate to={loginUrl} replace />
  }

  return jsx
}

export const withRouteWrapper = <Props extends object>(
  Component: ComponentType<Props>,
  routeMeta: RouteConfig['meta'] = {}
) => {
  const WrappedComponent = (props: Props) => (
    <RouteWrapper routeMeta={routeMeta}>
      <Component {...props} />
    </RouteWrapper>
  )
  WrappedComponent.displayName = `withRouteWrapper(${Component.displayName})`

  return WrappedComponent
}
