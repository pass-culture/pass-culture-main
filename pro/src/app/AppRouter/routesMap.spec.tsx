import { matchRoutes, type RouteObject } from 'react-router'

import { ADMIN_ROUTES } from './routes/administration'
import { ECOCONCEPTION_ROUTES } from './routes/ecoconception'
import { PARAMETRES_ROUTES } from './routes/parametres'
import { PARTENAIRE_ROUTES } from './routes/partenaire'
import { routes } from './routesMap'

export const APP_ROUTES = {
  HOME: '/',
  ...ADMIN_ROUTES,
  ...PARAMETRES_ROUTES,
  ...PARTENAIRE_ROUTES,
  ...ECOCONCEPTION_ROUTES,
} as const

function normalizePath(rawPath: string): string {
  return rawPath.replace(/\/+/g, '/').replace(/\/$/, '') || '/'
}

function extractFullRouterPaths(
  routes: RouteObject[],
  parentPath = ''
): string[] {
  return routes.flatMap((route) => {
    if (route.path === '*') {
      return []
    }

    if (route.index) {
      return [normalizePath(parentPath || '/')]
    }

    const currentPath = route.path
      ? route.path.startsWith('/')
        ? normalizePath(route.path)
        : normalizePath(`${parentPath}/${route.path}`)
      : normalizePath(parentPath || '/')

    const childPaths = route.children
      ? extractFullRouterPaths(route.children, currentPath)
      : []

    const hasIndexChild = route.children?.some((child) => child.index)
    const isLeafRoute = !route.children || route.children.length === 0
    const hasRenderableComponent = Boolean(
      route.element || route.Component || route.lazy
    )

    if (isLeafRoute && hasRenderableComponent) {
      return [currentPath]
    }

    if (
      !isLeafRoute &&
      hasRenderableComponent &&
      !hasIndexChild &&
      route.path
    ) {
      return [currentPath, ...childPaths]
    }

    return childPaths
  })
}

describe('Modular Router & APP_ROUTES consistency', () => {
  const routerPaths = new Set(extractFullRouterPaths(routes))
  const declaredConstants = Object.values(APP_ROUTES)

  it('should not have duplicate keys or paths across namespace route files', () => {
    const allNamespaceEntries = [['HOME', '/'], ...Object.entries(ADMIN_ROUTES)]

    const keys = allNamespaceEntries.map(([key]) => key)
    const paths = allNamespaceEntries.map(([, path]) => path)

    // Vérifie qu'aucun namespace n'écrase une clé existante lors du spread
    expect(new Set(keys).size).toBe(keys.length)
    // Vérifie que deux constantes différentes ne pointent pas vers la même URL
    expect(new Set(paths).size).toBe(paths.length)
  })

  it('should fail if a route in the router is not declared in any namespace', () => {
    const undeclaredRoutes = [...routerPaths].filter(
      (path) =>
        !declaredConstants.includes(path as (typeof declaredConstants)[number])
    )

    expect(undeclaredRoutes).toHaveLength(0)
    expect(undeclaredRoutes).toEqual([])
  })

  it('should fail if a route declared in a namespace is not mounted in the router', () => {
    const unmountedRoutes = declaredConstants.filter(
      (constantPath) => !routerPaths.has(constantPath)
    )

    expect(unmountedRoutes).toEqual([])
  })

  it.each(Object.values(APP_ROUTES))('should have the path %s', (path) => {
    expect(matchRoutes(routes, path)).not.toBeNull()
  })
})
