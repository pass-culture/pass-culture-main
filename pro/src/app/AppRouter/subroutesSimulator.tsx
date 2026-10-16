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
  },
  {
    lazy: () =>
      import('@/pages/Simulator/SimulatorOpenToPublic/SimulatorOpenToPublic'),

    loader: noop,
    path: '/inscription/preparation/accueil-public',
    handle: {
      title: 'Accueil du public',
    },
  },
  {
    lazy: () => import('@/pages/Simulator/SimulatorActivity/SimulatorActivity'),

    loader: noop,
    path: '/inscription/preparation/activite',
    handle: {
      title: 'Quelle est votre activité principale ?',
    },
  },
  {
    lazy: () => import('@/pages/Simulator/SimulatorTarget/SimulatorTarget'),
    loader: noop,
    path: '/inscription/preparation/publics',
    handle: {
      title: 'Quels publics souhaitez-vous cibler ?',
    },
  },
  {
    lazy: () => import('@/pages/Simulator/SimulatorResults/SimulatorResults'),
    loader: noop,
    path: '/inscription/preparation/resultats',
    handle: {
      title: 'Voici les justificatifs à préparer pour votre inscription',
    },
  },
  {
    lazy: () => import('@/pages/Simulator/SimulatorEmail/SimulatorEmail'),
    loader: noop,
    path: '/inscription/preparation/email',
    handle: {
      title: 'Recevez votre liste de justificatifs par email',
    },
  },
  {
    lazy: () =>
      import('@/pages/Simulator/SimulatorEmail/SimulatorEmailConfirmation'),
    loader: noop,
    path: '/inscription/preparation/email-confirmation',
    handle: {
      title: 'La liste de justificatifs a bien été envoyée par mail',
    },
  },
  {
    element: <Navigate to="/inscription/preparation/siret" />,
    loader: noop,
    path: '/inscription/preparation',
  },
]
