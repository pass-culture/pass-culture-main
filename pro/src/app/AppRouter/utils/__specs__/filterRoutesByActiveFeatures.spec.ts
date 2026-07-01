import type { RouteObject } from 'react-router'

import { filterRoutesByActiveFeatures } from '../filterRoutesByActiveFeatures'

type FeatureAwareRoute = RouteObject & {
  featureName?: string
  disabledWithFeatureName?: string
}

const buildRoutes = (): FeatureAwareRoute[] => [
  { path: '/always' },
  { path: '/gated', featureName: 'FF_1' },
  { path: '/disabled', disabledWithFeatureName: 'FF_2' },
  {
    path: '/parent',
    children: [
      { path: 'child-always' },
      { path: 'child-gated', featureName: 'FF_1' },
      { path: 'child-disabled', disabledWithFeatureName: 'FF_2' },
    ] as FeatureAwareRoute[],
  },
]

const getPaths = (routes: RouteObject[]): string[] =>
  routes.flatMap((route) => [
    ...(route.path ? [route.path] : []),
    ...(route.children ? getPaths(route.children) : []),
  ])

describe('filterRoutesByActiveFeatures', () => {
  it('should keep routes without any feature flag', () => {
    const result = filterRoutesByActiveFeatures(buildRoutes(), [])

    expect(getPaths(result)).toContain('/always')
    expect(getPaths(result)).toContain('child-always')
  })

  it('should remove routes gated behind an inactive featureName', () => {
    const result = filterRoutesByActiveFeatures(buildRoutes(), [])

    expect(getPaths(result)).not.toContain('/gated')
  })

  it('should keep routes gated behind an active featureName', () => {
    const result = filterRoutesByActiveFeatures(buildRoutes(), ['FF_1'])

    expect(getPaths(result)).toContain('/gated')
  })

  it('should remove routes disabled by an active disabledWithFeatureName', () => {
    const result = filterRoutesByActiveFeatures(buildRoutes(), ['FF_2'])

    expect(getPaths(result)).not.toContain('/disabled')
  })

  it('should filter nested children gated behind an inactive featureName', () => {
    const result = filterRoutesByActiveFeatures(buildRoutes(), [])

    expect(getPaths(result)).not.toContain('child-gated')
    expect(getPaths(result)).not.toContain('deep-gated')
  })

  it('should remove nested children disabled by an active disabledWithFeatureName', () => {
    const result = filterRoutesByActiveFeatures(buildRoutes(), ['FF_2'])

    expect(getPaths(result)).not.toContain('child-disabled')
  })
})
