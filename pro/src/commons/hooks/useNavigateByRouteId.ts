import { useCallback } from 'react'
import { useNavigate } from 'react-router'

import type { RouteId } from '@/app/AppRouter/constants'
import { routes } from '@/app/AppRouter/routesMap'

import { FrontendError } from '../errors/FrontendError'
import { handleUnexpectedError } from '../errors/handleUnexpectedError'

export const useNavigateByRouteId = () => {
  const navigate = useNavigate()

  const navigateByRouteId = useCallback(
    (routeId: RouteId) => {
      const route = routes.find((route) => route.id === routeId)
      if (!route) {
        handleUnexpectedError(
          new FrontendError(`route is undefined (routeId=${routeId}).`)
        )

        navigate('/error')

        return
      }

      navigate(route.path)
    },
    [navigate]
  )

  return navigateByRouteId
}
