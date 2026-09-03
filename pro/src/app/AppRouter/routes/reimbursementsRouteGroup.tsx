import { Navigate } from 'react-router'

import { withUserPermissions } from '@/commons/auth/withUserPermissions'
import { Reimbursements } from '@/pages/Reimbursements/Reimbursements'

import type { CustomRouteGroup } from '../types'
import { mustHaveSelectedAdminOfferer } from '../utils'

export const reimbursementsRouteGroup: CustomRouteGroup = {
  path: '/administration/remboursements',
  loader: withUserPermissions(mustHaveSelectedAdminOfferer),
  Component: Reimbursements,
  children: [
    {
      index: true,
      lazy: () =>
        import(
          '@/pages/Reimbursements/ReimbursementsInvoices/ReimbursementsInvoices'
        ),
      handle: {
        title: 'Gestion financière - justificatifs',
      },
    },
    {
      path: 'virements',
      lazy: () => import('@/pages/Reimbursements/Settlements/Settlements'),
      handle: {
        title: 'Gestion financière',
      },
      featureName: 'WIP_ENABLE_FINANCE_SETTLEMENTS',
    },
    // We keep a redirection here in case this link is still used in mail
    {
      path: 'justificatifs',
      element: <Navigate to="/administration/remboursements" replace />,
    },
    {
      path: 'informations-bancaires',
      lazy: () =>
        import('@/pages/Reimbursements/BankInformations/BankInformations'),
      handle: {
        title: 'Informations bancaires',
      },
    },
    {
      path: 'revenus',
      lazy: () => import('@/pages/Reimbursements/Income/Income'),
      handle: {
        title: 'Chiffre d’affaires',
      },
    },
  ],
}
