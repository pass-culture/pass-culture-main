/* No need to test this file */
/* istanbul ignore file */
import React from 'react'

import { Activity } from 'screens/SignupJourneyForm/Activity'
import { OffererAuthentication } from 'screens/SignupJourneyForm/Authentication'
import { ConfirmedAttachment } from 'screens/SignupJourneyForm/ConfirmedAttachment'
import { Offerer } from 'screens/SignupJourneyForm/Offerer'
import { Offerers as SignupJourneyOfferers } from 'screens/SignupJourneyForm/Offerers'
import { Validation } from 'screens/SignupJourneyForm/Validation'
import { Welcome } from 'screens/SignupJourneyForm/Welcome'

import type { IRoute } from './routesMap'

export const routesSignupJourney: IRoute[] = [
  {
    element: <Welcome />,
    parentPath: '/parcours-inscription',
    path: '/',
    title: "Parcours d'inscription",
  },
  {
    element: <Offerer />,
    parentPath: '/parcours-inscription',
    path: '/structure',
    title: 'Structure - Parcours d’inscription',
  },
  {
    element: <SignupJourneyOfferers />,
    parentPath: '/parcours-inscription',
    path: '/structure/rattachement',
    title: 'Rattachement à une structure - Parcours d’inscription',
  },
  {
    element: <ConfirmedAttachment />,
    parentPath: '/parcours-inscription',
    path: '/structure/rattachement/confirmation',
    title: 'Confirmation rattachement à une structure - Parcours d’inscription',
  },
  {
    element: <OffererAuthentication />,
    parentPath: '/parcours-inscription',
    path: '/identification',
    title: 'Identification - Parcours d’inscription',
  },
  {
    element: <Activity />,
    parentPath: '/parcours-inscription',
    path: '/activite',
    title: 'Activité - Parcours d’inscription',
  },
  {
    element: <Validation />,
    parentPath: '/parcours-inscription',
    path: '/validation',
    title: 'Validation - Parcours d’inscription',
  },
]

export default routesSignupJourney
