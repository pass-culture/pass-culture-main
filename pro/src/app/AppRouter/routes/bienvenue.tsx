import { withUserPermissions } from '@/commons/auth/withUserPermissions'

import type { CustomRouteGroup } from '../types'
import { mustBeUnauthenticated } from '../utils'

export const BIENVENUE_ROUTES = {
  BIENVENUE: '/bienvenue',
  BIENVENUE_PUBLICS: '/bienvenue/publics',
  BIENVENUE_OFFRES_JEUNES: '/bienvenue/offres-jeunes',
  BIENVENUE_OFFRES_SCOLAIRES: '/bienvenue/offres-scolaires',
  BIENVENUE_AVANTAGES: '/bienvenue/avantages',
  BIENVENUE_PROCHAINES_ETAPES: '/bienvenue/prochaines-etapes',
} as const

export const bienvenueRoutes: CustomRouteGroup['children'] = [
  {
    lazy: () => import('@/pages/WelcomeCarousel/WelcomeStepHub/WelcomeStepHub'),
    loader: withUserPermissions(mustBeUnauthenticated),
    index: true,
    handle: {
      title: 'Bienvenue sur pass Culture Pro',
    },
  },
  {
    lazy: () =>
      import('@/pages/WelcomeCarousel/WelcomeStepTarget/WelcomeStepTarget'),
    loader: withUserPermissions(mustBeUnauthenticated),
    path: 'publics',
    handle: {
      title: 'Deux manières de vous faire connaître',
    },
  },
  {
    lazy: () =>
      import(
        '@/pages/WelcomeCarousel/WelcomeStepIndividual/WelcomeStepIndividual'
      ),
    loader: withUserPermissions(mustBeUnauthenticated),
    path: 'offres-jeunes',
    handle: {
      title: 'Offres pour les jeunes via l’application',
    },
  },
  {
    lazy: () =>
      import(
        '@/pages/WelcomeCarousel/WelcomeStepCollective/WelcomeStepCollective'
      ),
    loader: withUserPermissions(mustBeUnauthenticated),
    path: 'offres-scolaires',
    handle: {
      title: 'Offres pour les groupes scolaires',
    },
  },
  {
    lazy: () =>
      import(
        '@/pages/WelcomeCarousel/WelcomeStepAdvantages/WelcomeStepAdvantages'
      ),
    loader: withUserPermissions(mustBeUnauthenticated),
    path: 'avantages',
    handle: {
      title: 'Pourquoi rejoindre le pass Culture ?',
    },
  },
  {
    lazy: () =>
      import(
        '@/pages/WelcomeCarousel/WelcomeStepNextSteps/WelcomeStepNextSteps'
      ),
    loader: withUserPermissions(mustBeUnauthenticated),
    path: 'prochaines-etapes',
    handle: {
      title: 'Comment fonctionne l’inscription ?',
    },
  },
]
