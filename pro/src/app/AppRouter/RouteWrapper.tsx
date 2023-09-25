import React, { ComponentType, ReactNode } from 'react'
import { Navigate, useLocation, useMatches } from 'react-router-dom'

import App from 'app/App/App'
import AppLayout from 'app/AppLayout'
import { RouteConfig } from 'app/AppRouter/routesMap'
import useCurrentUser from 'hooks/useCurrentUser'
import { dehumanizedRoute } from 'utils/dehumanize'

interface RouteWrapperProps {
  children: React.ReactNode
  routeMeta: RouteConfig['meta']
}

export const RouteWrapper = ({ children, routeMeta }: RouteWrapperProps) => {
  const { currentUser } = useCurrentUser()
  const location = useLocation()
  const matches = useMatches()
  const fromUrl = encodeURIComponent(`${location.pathname}${location.search}`)
  let jsx: ReactNode = children

  if (!routeMeta?.withoutLayout) {
    jsx = (
      <AppLayout layoutConfig={routeMeta && routeMeta.layoutConfig}>
        {jsx}
      </AppLayout>
    )
  }

  if (!routeMeta?.public && currentUser === null) {
    const loginUrl = fromUrl.includes('logout')
      ? '/connexion'
      : `/connexion?de=${fromUrl}`

    jsx = <Navigate to={loginUrl} replace />
  }

  // FIXME (mageoffray, 2023-03-24)
  // This is a temporary redirection to remove humanizedId.
  // For 6 months (until around 2023-10-01) we should redirect
  // urls with humanized params to url wih non human parameters
  /* istanbul ignore next */
  if (routeMeta?.shouldRedirect) {
    const newLocation = dehumanizedRoute(location, matches)
    if (location.pathname + location.search + location.hash != newLocation) {
      jsx = <Navigate to={newLocation} replace />
    }
  }
  return <App>{jsx}</App>
}

export const withRouteWrapper = <Props extends object>(
  Component: ComponentType<Props>,
  routeMeta: RouteConfig['meta']
) => {
  const WrappedComponent = (props: Props) => (
    <RouteWrapper routeMeta={routeMeta}>
      <Component {...props} />
    </RouteWrapper>
  )
  WrappedComponent.displayName = `withRouteWrapper(${Component.displayName})`

  return WrappedComponent
}
