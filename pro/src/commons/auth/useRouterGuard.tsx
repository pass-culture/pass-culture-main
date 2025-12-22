import { Navigate, useLocation } from 'react-router'

import { RouteId } from '@/app/AppRouter/constants'
import { findCurrentRoute } from '@/app/AppRouter/findCurrentRoute'
import { findRouteById } from '@/app/AppRouter/findRouteById'

import { FrontendError } from '../errors/FrontendError'
import { handleUnexpectedError } from '../errors/handleUnexpectedError'
import { useActiveFeature } from '../hooks/useActiveFeature'
import { useCurrentUserPermissions } from './useCurrentUserPermissions'

export const useRouterGuard = () => {
  const withSwitchVenueFeature = useActiveFeature('WIP_SWITCH_VENUE')

  const currentUserPermissions = useCurrentUserPermissions()
  const location = useLocation()

  if (!withSwitchVenueFeature) {
    return null
  }

  const currentRoute = findCurrentRoute(location)
  if (!currentRoute) {
    handleUnexpectedError(new FrontendError('`currentRoute` is undefined.'))

    return null
  }

  const isUserAllowedOnThisRoute = currentRoute.requiredPermissions(
    currentUserPermissions
  )
  if (isUserAllowedOnThisRoute) {
    return null
  }

  let redirectionRouteId: RouteId
  switch (true) {
    case !currentUserPermissions.isAuthenticated:
      redirectionRouteId = RouteId.Login
      break

    case !currentUserPermissions.hasSelectedVenue:
      redirectionRouteId = RouteId.Hub
      break

    case !currentUserPermissions.isSelectedVenueAssociated:
      redirectionRouteId = RouteId.PendingVenuAssociation
      break

    default:
      redirectionRouteId = RouteId.Homepage
      break
  }
  if (redirectionRouteId === currentRoute.id) {
    handleUnexpectedError(
      new FrontendError(
        'Impossible redirection to a route that forbids current user permissions.'
      ),
      {
        context: {
          currentRoute,
          currentUserPermissions,
          redirectionRouteId,
        },
      }
    )

    return null
  }

  return <Navigate to={findRouteById(redirectionRouteId).path} replace />
}
