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
    handle: {
      title: 'Structure - Parcours d’inscription',
    },
  },
  {
    element: <SignupJourneyOfferers />,
    loader: withUserPermissions(mustBeAuthenticated),
    path: '/inscription/structure/rattachement',
    handle: {
      title: 'Rattachement à une structure - Parcours d’inscription',
    },
  },
  {
    element: <ConfirmedAttachment />,
    loader: withUserPermissions(mustBeAuthenticated),
    path: '/inscription/structure/rattachement/confirmation-rattachement',
    handle: {
      title:
        'Confirmation rattachement à une structure - Parcours d’inscription',
    },
  },
  {
    element: <OffererAuthentication />,
    loader: withUserPermissions(mustBeAuthenticated),
    path: '/inscription/structure/identification',
    handle: {
      title: 'Identification - Parcours d’inscription',
    },
  },
  {
    element: <Activity />,
    loader: withUserPermissions(mustBeAuthenticated),
    path: '/inscription/structure/activite',
    handle: {
      title: 'Activité - Parcours d’inscription',
    },
  },
  {
    element: <Validation />,
    loader: withUserPermissions(mustBeAuthenticated),
    path: '/inscription/structure/confirmation',
    handle: {
      title: 'Validation - Parcours d’inscription',
    },
  },
]
