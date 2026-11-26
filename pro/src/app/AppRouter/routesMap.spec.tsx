import { matchRoutes, type RouteObject } from 'react-router'

import { ADMIN_ROUTES } from './routes/administration'
import { BIENVENUE_ROUTES, bienvenueRoutes } from './routes/bienvenue'
import { ECOCONCEPTION_ROUTES } from './routes/ecoconception'
import { INSCRIPTION_ROUTES, inscriptionRoutes } from './routes/inscription'
import {
  INSCRIPTION_PREPARATION_ROUTES,
  inscriptionPreparationRoutes,
} from './routes/inscriptionPreparation'
import {
  INSCRIPTION_STRUCTURE_ROUTES,
  inscriptionStructureRoutes,
} from './routes/inscriptionStructure'
import {
  OFFRE_INDIVIDUELLE_ROUTES,
  offreIndividuelleRoutes,
} from './routes/offreIndividuelle'
import {
  OFFRE_INDIVIDUELLE_V2_ROUTES,
  offreIndividuelleV2Routes,
} from './routes/offreIndividuelleV2'
import {
  ONBOARDING_OFFRE_INDIVIDUELLE_ROUTES,
  onboardingOffreIndividuelleRoutes,
} from './routes/onboardingOffreIndividuelle'
import { PARAMETRES_ROUTES } from './routes/parametres'
import { PARTENAIRE_ROUTES } from './routes/partenaire'
import { routes } from './routesMap'

const namespaceConstants = [
  { HOME: '/' },
  ADMIN_ROUTES,
  PARAMETRES_ROUTES,
  PARTENAIRE_ROUTES,
  ECOCONCEPTION_ROUTES,
  BIENVENUE_ROUTES,
  INSCRIPTION_ROUTES,
  INSCRIPTION_PREPARATION_ROUTES,
  INSCRIPTION_STRUCTURE_ROUTES,
  OFFRE_INDIVIDUELLE_ROUTES,
  OFFRE_INDIVIDUELLE_V2_ROUTES,
  ONBOARDING_OFFRE_INDIVIDUELLE_ROUTES,
]

export const APP_ROUTES = {
  HOME: '/',
  ...ADMIN_ROUTES,
  ...PARAMETRES_ROUTES,
  ...PARTENAIRE_ROUTES,
  ...ECOCONCEPTION_ROUTES,
  ...BIENVENUE_ROUTES,
  ...INSCRIPTION_ROUTES,
  ...INSCRIPTION_PREPARATION_ROUTES,
  ...INSCRIPTION_STRUCTURE_ROUTES,
  ...OFFRE_INDIVIDUELLE_ROUTES,
  ...OFFRE_INDIVIDUELLE_V2_ROUTES,
  ...ONBOARDING_OFFRE_INDIVIDUELLE_ROUTES,
} as const

function normalizePath(rawPath: string): string {
  return rawPath.replace(/\/+/g, '/').replace(/\/$/, '') || '/'
}

function extractFullRouterPaths(
  routes: RouteObject[],
  parentPath = ''
): string[] {
  return routes.flatMap((route) => {
    if (route.path === '*' || route.path?.endsWith('/*')) {
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

    return route.path ? [currentPath, ...childPaths] : childPaths
  })
}

describe('Modular Router & APP_ROUTES consistency', () => {
  const routerPaths = new Set(extractFullRouterPaths(routes))
  const declaredConstants = Object.values(APP_ROUTES)

  it('should not have duplicate keys or paths across namespace route files', () => {
    const allNamespaceEntries = namespaceConstants.flatMap((constants) =>
      Object.entries(constants)
    )

    const keys = allNamespaceEntries.map(([key]) => key)
    const paths = allNamespaceEntries.map(([, path]) => path)

    // Vérifie qu'aucun namespace n'écrase une clé existante lors du spread
    expect(new Set(keys).size).toBe(keys.length)
    // Vérifie que deux constantes différentes ne pointent pas vers la même URL
    expect(new Set(paths).size).toBe(paths.length)
  })

  describe('Migrated namespace constants', () => {
    it.each([
      {
        prefix: '/bienvenue',
        children: bienvenueRoutes,
        constants: BIENVENUE_ROUTES,
      },
      {
        prefix: '/inscription',
        children: inscriptionRoutes,
        constants: INSCRIPTION_ROUTES,
      },
      {
        prefix: '/inscription/preparation',
        children: inscriptionPreparationRoutes,
        constants: INSCRIPTION_PREPARATION_ROUTES,
      },
      {
        prefix: '/inscription/structure',
        children: inscriptionStructureRoutes,
        constants: INSCRIPTION_STRUCTURE_ROUTES,
      },
      {
        prefix: '/offre/individuelle',
        children: offreIndividuelleRoutes,
        constants: OFFRE_INDIVIDUELLE_ROUTES,
      },
      {
        prefix: '/offre/individuelle/v2',
        children: offreIndividuelleV2Routes,
        constants: OFFRE_INDIVIDUELLE_V2_ROUTES,
      },
      {
        prefix: '/onboarding/offre/individuelle',
        children: onboardingOffreIndividuelleRoutes,
        constants: ONBOARDING_OFFRE_INDIVIDUELLE_ROUTES,
      },
    ])(
      'should declare every full path for $prefix',
      ({ prefix, children, constants }) => {
        const parent = routes.find((route) => route.path === prefix)
        expect(parent?.children).toBe(children)
        expect(children.every((route) => !route.path?.startsWith('/'))).toBe(
          true
        )

        const expectedPaths = new Set([
          prefix,
          ...extractFullRouterPaths(children, prefix),
        ])
        expect(new Set(Object.values(constants))).toEqual(expectedPaths)
        expect(Object.values(constants)).toHaveLength(expectedPaths.size)
      }
    )
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
