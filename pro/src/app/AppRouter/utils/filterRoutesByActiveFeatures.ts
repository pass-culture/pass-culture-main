import type { RouteObject } from 'react-router'

type FeatureAwareRoute = RouteObject & {
  featureName?: string
  disabledWithFeatureName?: string
}

const isRouteActive = (
  route: FeatureAwareRoute,
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
  routes: FeatureAwareRoute[],
  activeFeatures: string[]
): RouteObject[] =>
  routes
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
