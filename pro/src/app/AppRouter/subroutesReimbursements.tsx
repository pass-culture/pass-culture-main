/* No need to test this file */
/* istanbul ignore file */
import React from 'react'

import BankInformations from 'pages/Reimbursements/BankInformations/BankInformations'
import ReimbursementsDetails from 'pages/Reimbursements/ReimbursementsDetails/ReimbursementsDetails'
import { ReimbursementsInvoices } from 'pages/Reimbursements/ReimbursementsInvoices'

import type { RouteConfig } from './routesMap'

export const routesReimbursements: RouteConfig[] = [
  {
    element: <ReimbursementsInvoices />,
    path: '/remboursements/justificatifs',
    title: 'Justificatifs',
  },
  {
    element: <ReimbursementsDetails />,
    path: '/remboursements/details',
    title: 'Détails',
  },
  {
    element: <BankInformations />,
    path: '/remboursements/informations-bancaires',
    title: 'Informations bancaires',
    featureName: 'WIP_ENABLE_NEW_BANK_DETAILS_JOURNEY',
  },
]
