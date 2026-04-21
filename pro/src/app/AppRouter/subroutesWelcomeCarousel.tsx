/* No need to test this file */
/* istanbul ignore file */

import { withUserPermissions } from '@/commons/auth/withUserPermissions'

import type { CustomRouteGroupChild } from './types'
import { mustBeUnauthenticated } from './utils'

export const routesWelcomeCarousel: CustomRouteGroupChild[] = [
  {
    lazy: () => import('@/pages/WelcomeCarousel/WelcomeStepHub/WelcomeStepHub'),
    loader: withUserPermissions(mustBeUnauthenticated),
    path: '/bienvenue',
    title: 'Bienvenue sur pass Culture Pro',
  },
  {
    lazy: () =>
      import('@/pages/WelcomeCarousel/WelcomeStepTarget/WelcomeStepTarget'),
    loader: withUserPermissions(mustBeUnauthenticated),
    path: '/bienvenue/publics',
    title: 'Deux manières de vous faire connaître',
  },
  {
    lazy: () =>
      import(
        '@/pages/WelcomeCarousel/WelcomeStepIndividual/WelcomeStepIndividual'
      ),
    loader: withUserPermissions(mustBeUnauthenticated),
    path: '/bienvenue/offres-jeunes',
    title: 'Offres pour les jeunes via l’application',
  },
  {
    lazy: () =>
      import(
        '@/pages/WelcomeCarousel/WelcomeStepCollective/WelcomeStepCollective'
      ),
    loader: withUserPermissions(mustBeUnauthenticated),
    path: '/bienvenue/offres-scolaires',
    title: 'Offres pour les groupes scolaires',
  },
  {
    lazy: () =>
      import(
        '@/pages/WelcomeCarousel/WelcomeStepAdvantages/WelcomeStepAdvantages'
      ),
    loader: withUserPermissions(mustBeUnauthenticated),
    path: '/bienvenue/avantages',
    title: 'Pourquoi rejoindre le pass Culture ?',
  },
  {
    lazy: () =>
      import(
        '@/pages/WelcomeCarousel/WelcomeStepNextSteps/WelcomeStepNextSteps'
      ),
    loader: withUserPermissions(mustBeUnauthenticated),
    path: '/bienvenue/prochaines-etapes',
    title: 'Comment fonctionne l’inscription ?',
  },
]
