/* No need to test this file */
/* istanbul ignore file */

import { Navigate } from 'react-router'

import { withUserPermissions } from '@/commons/auth/withUserPermissions'
import { BankInformations } from '@/pages/Reimbursements/BankInformations/BankInformations'
import { Income } from '@/pages/Reimbursements/Income/Income'
import { ReimbursementsInvoices } from '@/pages/Reimbursements/ReimbursementsInvoices/ReimbursementsInvoices'

import type { CustomRouteObject } from './types'
import { mustHaveSelectedAdminOfferer } from './utils'

export const routesReimbursements: CustomRouteObject[] = [
  {
    element: <ReimbursementsInvoices />,
    loader: withUserPermissions(mustHaveSelectedAdminOfferer),
    path: '/remboursements',
    title: 'Gestion financière - justificatifs',
  },
  // We keep a redirection here in case this link is still used in mail
  {
    element: <Navigate to="/remboursements" />,
    loader: withUserPermissions(mustHaveSelectedAdminOfferer),
    path: '/remboursements/justificatifs',
    title: 'Gestion financière',
  },
  {
    element: <BankInformations />,
    loader: withUserPermissions(mustHaveSelectedAdminOfferer),
    path: '/remboursements/informations-bancaires',
    title: 'Informations bancaires',
  },
  {
    element: <Income />,
    loader: withUserPermissions(mustHaveSelectedAdminOfferer),
    path: '/remboursements/revenus',
    title: 'Chiffre d’affaires',
  },
]
