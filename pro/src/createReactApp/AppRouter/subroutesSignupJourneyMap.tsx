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
    title: '',
  },
  {
    element: <Offerer />,
    parentPath: '/parcours-inscription',
    path: '/structure',
    title: '',
  },
  {
    element: <SignupJourneyOfferers />,
    parentPath: '/parcours-inscription',
    path: '/structure/rattachement',
    title: '',
  },
  {
    element: <ConfirmedAttachment />,
    parentPath: '/parcours-inscription',
    path: '/structure/rattachement/confirmation',
    title: '',
  },
  {
    element: <OffererAuthentication />,
    parentPath: '/parcours-inscription',
    path: '/authentification',
    title: '',
  },
  {
    element: <OffererAuthentication />,
    parentPath: '/parcours-inscription',
    path: '/authentification',
    title: '',
  },
  {
    element: <Activity />,
    parentPath: '/parcours-inscription',
    path: '/activite',
    title: '',
  },
  {
    element: <Validation />,
    parentPath: '/parcours-inscription',
    path: '/validation',
    title: '',
  },
]

export default routesSignupJourney
