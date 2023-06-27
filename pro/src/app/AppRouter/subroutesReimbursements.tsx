/* No need to test this file */
/* istanbul ignore file */
import React from 'react'

import ReimbursementsDetails from 'pages/Reimbursements/ReimbursementsDetails/ReimbursementsDetails'
import { ReimbursementsInvoices } from 'pages/Reimbursements/ReimbursementsInvoices'

import type { RouteConfig } from './routesMap'

export const routesReimbursements: RouteConfig[] = [
  {
    element: <ReimbursementsInvoices />,
    parentPath: '/remboursements',
    path: '/justificatifs',
    title: 'Justificatifs des remboursements',
  },
  {
    element: <ReimbursementsDetails />,
    parentPath: '/remboursements',
    path: '/details',
    title: 'Détails des remboursements',
  },
]
