/* No need to test this file */
/* istanbul ignore file */
import React from 'react'
import { Navigate } from 'react-router'

import { BankInformations } from 'pages/Reimbursements/BankInformations/BankInformations'
import { ReimbursementsInvoices } from 'pages/Reimbursements/ReimbursementsInvoices/ReimbursementsInvoices'

import type { RouteConfig } from './routesMap'

export const routesReimbursements: RouteConfig[] = [
  {
    element: <ReimbursementsInvoices />,
    path: '/remboursements',
    title: 'Gestion financière',
  },
  // We keep a redirection here in case this link is still used in mail
  {
    element: <Navigate to="/remboursements" />,
    path: '/remboursements/justificatifs',
    title: 'Gestion financière',
  },
  {
    element: <BankInformations />,
    path: '/remboursements/informations-bancaires',
    title: 'Informations bancaires',
  },
]
