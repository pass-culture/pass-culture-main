import { withUserPermissions } from '@/commons/auth/withUserPermissions'

import type { CustomRouteGroupChild } from './types'
import { mustBeAuthenticated } from './utils'

export const routesSignupJourney: CustomRouteGroupChild[] = [
  {
    lazy: async () => ({
      Component: (
        await import('@/components/SignupJourneyForm/Offerer/Offerer')
      ).Offerer,
    }),
    loader: withUserPermissions(mustBeAuthenticated),
    path: 'recherche',
    handle: {
      title: 'Structure - Parcours d’inscription',
    },
  },
  {
    lazy: async () => ({
      Component: (
        await import('@/components/SignupJourneyForm/Offerers/Offerers')
      ).Offerers,
    }),
    loader: withUserPermissions(mustBeAuthenticated),
    path: 'rattachement',
    handle: {
      title: 'Rattachement à une structure - Parcours d’inscription',
    },
  },
  {
    lazy: async () => ({
      Component: (
        await import(
          '@/components/SignupJourneyForm/ConfirmedAttachment/ConfirmedAttachment'
        )
      ).ConfirmedAttachment,
    }),
    loader: withUserPermissions(mustBeAuthenticated),
    path: 'rattachement/confirmation-rattachement',
    handle: {
      title:
        'Confirmation rattachement à une structure - Parcours d’inscription',
    },
  },
  {
    lazy: async () => ({
      Component: (
        await import(
          '@/components/SignupJourneyForm/Authentication/OffererAuthentication'
        )
      ).OffererAuthentication,
    }),
    loader: withUserPermissions(mustBeAuthenticated),
    path: 'identification',
    handle: {
      title: 'Identification - Parcours d’inscription',
    },
  },
  {
    lazy: async () => ({
      Component: (
        await import('@/components/SignupJourneyForm/Activity/Activity')
      ).Activity,
    }),
    loader: withUserPermissions(mustBeAuthenticated),
    path: 'activite',
    handle: {
      title: 'Activité - Parcours d’inscription',
    },
  },
  {
    lazy: async () => ({
      Component: (
        await import('@/components/SignupJourneyForm/Validation/Validation')
      ).Validation,
    }),
    loader: withUserPermissions(mustBeAuthenticated),
    path: 'confirmation',
    handle: {
      title: 'Validation - Parcours d’inscription',
    },
  },
]
