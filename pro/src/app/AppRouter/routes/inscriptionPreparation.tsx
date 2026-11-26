import { Navigate } from 'react-router'

import { noop } from '@/commons/utils/noop'

import type { CustomRouteGroup } from '../types'

export const INSCRIPTION_PREPARATION_ROUTES = {
  INSCRIPTION_PREPARATION: '/inscription/preparation',
  INSCRIPTION_PREPARATION_SIRET: '/inscription/preparation/siret',
  INSCRIPTION_PREPARATION_ACCUEIL_PUBLIC:
    '/inscription/preparation/accueil-public',
  INSCRIPTION_PREPARATION_ACTIVITE: '/inscription/preparation/activite',
  INSCRIPTION_PREPARATION_PUBLICS: '/inscription/preparation/publics',
  INSCRIPTION_PREPARATION_RESULTATS: '/inscription/preparation/resultats',
  INSCRIPTION_PREPARATION_EMAIL: '/inscription/preparation/email',
  INSCRIPTION_PREPARATION_EMAIL_CONFIRMATION:
    '/inscription/preparation/email-confirmation',
} as const

export const inscriptionPreparationRoutes: CustomRouteGroup['children'] = [
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
