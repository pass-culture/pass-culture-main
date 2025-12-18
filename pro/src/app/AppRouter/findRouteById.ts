import { assertOrFrontendError } from '@/commons/errors/assertOrFrontendError'

import type { RouteId } from './constants'
import { routes } from './routesMap'
import type { CustomRouteObject } from './types'

export const findRouteById = (id: RouteId): CustomRouteObject => {
  const route = routes.find((route) => route.id === id)
  assertOrFrontendError(route, `route not found for ID-"${id}".`)

  return route
}
