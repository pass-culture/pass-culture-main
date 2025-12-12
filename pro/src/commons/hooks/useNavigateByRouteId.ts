import { useCallback } from 'react'
import { useNavigate } from 'react-router'

import type { RouteId } from '@/app/AppRouter/constants'
import { routes } from '@/app/AppRouter/routesMap'

import { assertOrFrontendError } from '../errors/assertOrFrontendError'

export const useNavigateByRouteId = () => {
  const navigate = useNavigate()

  const navigateByRouteId = useCallback(
    (routeId: RouteId) => {
      const route = routes.find((route) => route.id === routeId)
      assertOrFrontendError(route, `route is undefined (routeId=${routeId}).`)

      navigate(route.path)
    },
    [navigate]
  )

  return navigateByRouteId
}
