/* No need to test this file */
/* istanbul ignore file */
import React from 'react'

import BankInformations from 'pages/Reimbursements/BankInformations/BankInformations'
import ReimbursementsDetails from 'pages/Reimbursements/ReimbursementsDetails/ReimbursementsDetails'
import { ReimbursementsInvoices } from 'pages/Reimbursements/ReimbursementsInvoices'

import type { RouteConfig } from './routesMap'

// TODO: Remove after WIP_ENABLE_NEW_BANK_DETAILS_JOURNEY deleted
export const oldRoutesReimbursements: RouteConfig[] = [
  {
    element: <ReimbursementsInvoices />,
    parentPath: '/remboursements',
    path: '/justificatifs',
    title: 'Justificatifs des remboursements',
  },
  {
    element: <ReimbursementsDetails />,
    parentPath: '/remboursements',
    path: 'Détails des remboursements',
  },
]

export const routesReimbursements: RouteConfig[] = [
  {
    element: <ReimbursementsInvoices />,
    parentPath: '/remboursements',
    path: '/justificatifs',
    title: 'Justificatifs',
  },
  {
    element: <ReimbursementsDetails />,
    parentPath: '/remboursements',
    path: '/details',
    title: 'Détails',
  },
  {
    element: <BankInformations />,
    parentPath: '/remboursements',
    path: '/informations-bancaires',
    title: 'Informations bancaires',
    featureName: 'WIP_ENABLE_NEW_BANK_DETAILS_JOURNEY',
  },
]
