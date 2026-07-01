import type { RouteObject } from 'react-router'

import type { CustomRouteTree } from '../types'

const isRouteActive = (
  route: CustomRouteTree[number],
  activeFeatures: string[]
): boolean => {
  if (
    route.disabledWithFeatureName &&
    activeFeatures.includes(route.disabledWithFeatureName)
  ) {
    return false
  }

  return !route.featureName || activeFeatures.includes(route.featureName)
}

// Filter routes based on active features recursively for nested children
export const filterRoutesByActiveFeatures = (
  routes: RouteObject[],
  activeFeatures: string[]
): CustomRouteTree =>
  (routes as CustomRouteTree)
    .filter((route) => isRouteActive(route, activeFeatures))
    .map((route) =>
      route.children
        ? {
            ...route,
            children: filterRoutesByActiveFeatures(
              route.children,
              activeFeatures
            ),
          }
        : route
    )
