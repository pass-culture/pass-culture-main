/* No need to test this file */
/* istanbul ignore file */

import { withUserPermissions } from '@/commons/auth/withUserPermissions'
import { Activity } from '@/components/SignupJourneyForm/Activity/Activity'
import { OffererAuthentication } from '@/components/SignupJourneyForm/Authentication/OffererAuthentication'
import { ConfirmedAttachment } from '@/components/SignupJourneyForm/ConfirmedAttachment/ConfirmedAttachment'
import { Offerer } from '@/components/SignupJourneyForm/Offerer/Offerer'
import { Offerers as SignupJourneyOfferers } from '@/components/SignupJourneyForm/Offerers/Offerers'
import { Validation } from '@/components/SignupJourneyForm/Validation/Validation'

import type { CustomRouteGroupChild } from './types'
import { mustBeAuthenticated } from './utils'

export const routesSignupJourney: CustomRouteGroupChild[] = [
  {
    element: <Offerer />,
    loader: withUserPermissions(mustBeAuthenticated),
    path: '/inscription/structure/recherche',
    title: 'Structure - Parcours d’inscription',
    meta: {
      canBeUnattached: true,
    },
  },
  {
    element: <SignupJourneyOfferers />,
    loader: withUserPermissions(mustBeAuthenticated),
    path: '/inscription/structure/rattachement',
    title: 'Rattachement à une structure - Parcours d’inscription',
    meta: {
      canBeUnattached: true,
    },
  },
  {
    element: <ConfirmedAttachment />,
    loader: withUserPermissions(mustBeAuthenticated),
    path: '/inscription/structure/rattachement/confirmation',
    title: 'Confirmation rattachement à une structure - Parcours d’inscription',
    meta: {
      canBeUnattached: true,
    },
  },
  {
    element: <OffererAuthentication />,
    loader: withUserPermissions(mustBeAuthenticated),
    path: '/inscription/structure/identification',
    title: 'Identification - Parcours d’inscription',
    meta: {
      canBeUnattached: true,
    },
  },
  {
    element: <Activity />,
    loader: withUserPermissions(mustBeAuthenticated),
    path: '/inscription/structure/activite',
    title: 'Activité - Parcours d’inscription',
    meta: {
      canBeUnattached: true,
    },
  },
  {
    element: <Validation />,
    loader: withUserPermissions(mustBeAuthenticated),
    path: '/inscription/structure/confirmation',
    title: 'Validation - Parcours d’inscription',
    meta: {
      canBeUnattached: true,
    },
  },
]
