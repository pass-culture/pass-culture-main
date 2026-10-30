import { Navigate } from 'react-router'

import { noop } from '@/commons/utils/noop'

import type { CustomRouteGroup } from './types'

export const routesSimulator: CustomRouteGroup['children'] = [
  {
    index: true,
    element: <Navigate to="/inscription/preparation/siret" />,
    loader: noop,
  },
  {
    lazy: () => import('@/pages/Simulator/SimulatorSiret/SimulatorSiret'),
    loader: noop,
    path: 'siret',
    handle: {
      title: 'Renseignez votre SIRET',
    },
  },
  {
    lazy: () =>
      import('@/pages/Simulator/SimulatorOpenToPublic/SimulatorOpenToPublic'),

    loader: noop,
    path: 'accueil-public',
    handle: {
      title: 'Accueil du public',
    },
  },
  {
    lazy: () => import('@/pages/Simulator/SimulatorActivity/SimulatorActivity'),

    loader: noop,
    path: 'activite',
    handle: {
      title: 'Quelle est votre activité principale ?',
    },
  },
  {
    lazy: () => import('@/pages/Simulator/SimulatorTarget/SimulatorTarget'),
    loader: noop,
    path: 'publics',
    handle: {
      title: 'Quels publics souhaitez-vous cibler ?',
    },
  },
  {
    lazy: () => import('@/pages/Simulator/SimulatorResults/SimulatorResults'),
    loader: noop,
    path: 'resultats',
    handle: {
      title: 'Voici les justificatifs à préparer pour votre inscription',
    },
  },
  {
    lazy: () => import('@/pages/Simulator/SimulatorEmail/SimulatorEmail'),
    loader: noop,
    path: 'email',
    handle: {
      title: 'Recevez votre liste de justificatifs par email',
    },
  },
  {
    lazy: () =>
      import('@/pages/Simulator/SimulatorEmail/SimulatorEmailConfirmation'),
    loader: noop,
    path: 'email-confirmation',
    handle: {
      title: 'La liste de justificatifs a bien été envoyée par mail',
    },
  },
]
