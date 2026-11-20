import { Reimbursements } from '@/pages/Reimbursements/Reimbursements'

import type { CustomRouteGroup } from '../types'
import {
  ADMIN_REIMBURSEMENT,
  administrationReimbursementsRoutes,
} from './administrationReimbursements'

export const ADMIN_ROUTES = {
  ...ADMIN_REIMBURSEMENT,
  ADMIN_COLLABS: '/administration/collaborateurs',
  ADMIN_ACTIVITES_INDIVIDUEL: '/administration/donnees-activite/individuel',
  ADMIN_ACTIVITES_COLLECTIF: '/administration/donnees-activite/collectif',
} as const

export const administrationRoutes: CustomRouteGroup['children'] = [
  {
    path: 'gestion-financiere',
    Component: Reimbursements,
    children: administrationReimbursementsRoutes,
  },
  {
    path: 'collaborateurs',
    handle: {
      title: 'Collaborateurs',
    },
    lazy: () => import('@/pages/Collaborators/Collaborators'),
  },
  {
    path: 'donnees-activite/individuel',
    handle: {
      title: "Données d'activité : individuel",
    },
    lazy: () => import('@/pages/IndividualActivityData/IndividualActivityData'),
  },
  {
    path: 'donnees-activite/collectif',
    handle: {
      title: "Données d'activité : collectif",
    },
    lazy: () => import('@/pages/CollectiveActivityData/CollectiveActivityData'),
  },
]
