/* No need to test this file */
/* istanbul ignore file */
import React from 'react'

import { Activity } from 'screens/SignupJourneyForm/Activity/Activity'
import { OffererAuthentication } from 'screens/SignupJourneyForm/Authentication/OffererAuthentication'
import { ConfirmedAttachment } from 'screens/SignupJourneyForm/ConfirmedAttachment/ConfirmedAttachment'
import { Offerer } from 'screens/SignupJourneyForm/Offerer/Offerer'
import { Offerers as SignupJourneyOfferers } from 'screens/SignupJourneyForm/Offerers/Offerers'
import { Validation } from 'screens/SignupJourneyForm/Validation/Validation'
import { Welcome } from 'screens/SignupJourneyForm/Welcome/Welcome'

import type { RouteConfig } from './routesMap'

export const routesSignupJourney: RouteConfig[] = [
  {
    element: <Welcome />,
    path: '/parcours-inscription',
    title: 'Parcours d’inscription',
  },
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
