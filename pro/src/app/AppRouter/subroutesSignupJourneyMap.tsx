/* No need to test this file */
/* istanbul ignore file */
import { Activity } from 'components/SignupJourneyForm/Activity/Activity'
import { OffererAuthentication } from 'components/SignupJourneyForm/Authentication/OffererAuthentication'
import { ConfirmedAttachment } from 'components/SignupJourneyForm/ConfirmedAttachment/ConfirmedAttachment'
import { Offerer } from 'components/SignupJourneyForm/Offerer/Offerer'
import { Offerers as SignupJourneyOfferers } from 'components/SignupJourneyForm/Offerers/Offerers'
import { Validation } from 'components/SignupJourneyForm/Validation/Validation'

import type { RouteConfig } from './routesMap'

export const routesSignupJourney: RouteConfig[] = [
  {
    element: <Offerer />,
    path: '/parcours-inscription/structure',
    title: 'Structure - Parcours d’inscription',
  },
  {
    element: <SignupJourneyOfferers />,
    path: '/parcours-inscription/structure/rattachement',
    title: 'Rattachement à une structure - Parcours d’inscription',
  },
  {
    element: <ConfirmedAttachment />,
    path: '/parcours-inscription/structure/rattachement/confirmation',
    title: 'Confirmation rattachement à une structure - Parcours d’inscription',
  },
  {
    element: <OffererAuthentication />,
    path: '/parcours-inscription/identification',
    title: 'Identification - Parcours d’inscription',
  },
  {
    element: <Activity />,
    path: '/parcours-inscription/activite',
    title: 'Activité - Parcours d’inscription',
  },
  {
    element: <Validation />,
    path: '/parcours-inscription/validation',
    title: 'Validation - Parcours d’inscription',
  },
]
