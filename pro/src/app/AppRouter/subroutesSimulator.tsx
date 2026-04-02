/* No need to test this file */
/* istanbul ignore file */

import { Navigate } from 'react-router'

import { noop } from '@/commons/utils/noop'

import type { CustomRouteGroupChild } from './types'

export const routesSimulator: CustomRouteGroupChild[] = [
  {
    lazy: () => import('@/pages/Simulator/SimulatorSiret/SimulatorSiret'),
    loader: noop,
    path: '/inscription/preparation/siret',
    handle: {
      title: 'Renseignez votre SIRET',
    },
    featureName: 'WIP_PRE_SIGNUP_SIMULATION',
    meta: { public: true },
  },
  {
    lazy: () => import('@/pages/Simulator/SimulatorActivity/SimulatorActivity'),

    loader: noop,
    path: '/inscription/preparation/activite',
    handle: {
      title: 'Quelle est votre activité principale ?',
    },
    featureName: 'WIP_PRE_SIGNUP_SIMULATION',
    meta: { public: true },
  },
  {
    lazy: () => import('@/pages/Simulator/SimulatorTarget/SimulatorTarget'),
    loader: noop,
    path: '/inscription/preparation/publics',
    handle: {
      title: 'Quels publics souhaitez-vous cibler ?',
    },
    featureName: 'WIP_PRE_SIGNUP_SIMULATION',
    meta: { public: true },
  },
  {
    lazy: () => import('@/pages/Simulator/SimulatorResults/SimulatorResults'),
    loader: noop,
    path: '/inscription/preparation/resultats',
    handle: {
      title: 'Voici les justificatifs à préparer pour votre inscription',
    },
    featureName: 'WIP_PRE_SIGNUP_SIMULATION',
    meta: { public: true },
  },
  {
    element: <Navigate to="/inscription/preparation/siret" />,
    loader: noop,
    path: '/inscription/preparation',
    featureName: 'WIP_PRE_SIGNUP_SIMULATION',
    meta: { public: true },
  },
]
