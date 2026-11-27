import { withUserPermissions } from '@/commons/auth/withUserPermissions'

import type { CustomRouteGroupChild } from './types'
import { mustBeAuthenticated } from './utils'

export const routesSignupJourney: CustomRouteGroupChild[] = [
  {
    lazy: () => import('@/components/SignupJourneyForm/Offerer/Offerer'),
    loader: withUserPermissions(mustBeAuthenticated),
    path: 'recherche',
    handle: {
      title: 'Structure - Parcours d’inscription',
    },
  },
  {
    lazy: () => import('@/components/SignupJourneyForm/Offerers/Offerers'),
    loader: withUserPermissions(mustBeAuthenticated),
    path: 'rattachement',
    handle: {
      title: 'Rattachement à une structure - Parcours d’inscription',
    },
  },
  {
    lazy: () =>
      import(
        '@/components/SignupJourneyForm/ConfirmedAttachment/ConfirmedAttachment'
      ),
    loader: withUserPermissions(mustBeAuthenticated),
    path: 'rattachement/confirmation-rattachement',
    handle: {
      title:
        'Confirmation rattachement à une structure - Parcours d’inscription',
    },
  },
  {
    lazy: () =>
      import(
        '@/components/SignupJourneyForm/Authentication/OffererAuthentication'
      ),
    loader: withUserPermissions(mustBeAuthenticated),
    path: 'identification',
    handle: {
      title: 'Identification - Parcours d’inscription',
    },
  },
  {
    lazy: () => import('@/components/SignupJourneyForm/Activity/Activity'),
    loader: withUserPermissions(mustBeAuthenticated),
    path: 'activite',
    handle: {
      title: 'Activité - Parcours d’inscription',
    },
  },
  {
    lazy: () => import('@/components/SignupJourneyForm/Validation/Validation'),
    loader: withUserPermissions(mustBeAuthenticated),
    path: 'confirmation',
    handle: {
      title: 'Validation - Parcours d’inscription',
    },
  },
]
