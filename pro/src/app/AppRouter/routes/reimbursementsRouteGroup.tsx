import { Navigate } from 'react-router'

import { withUserPermissions } from '@/commons/auth/withUserPermissions'
import { Reimbursements } from '@/pages/Reimbursements/Reimbursements'

import type { CustomRouteGroup } from '../types'
import { mustHaveSelectedAdminOfferer } from '../utils'

// TODO (igabriele, 2026-02-10): Move that within `administrationRouteGroup` once `WIP_SWITCH_VENUE` FF is enabled and removed:
// 1. `<Reimbursements />` within `<AdministrationLayout />`
// 2. Merge this route group into `administrationRouteGroup`
// 3. Prefix these paths with `administration/`
// 4. Maybe move `@/pages/Reimbursements/*` pages at the top level of `@/pages`?
export const reimbursementsRouteGroup: CustomRouteGroup = {
  path: '/remboursements',
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
    // We keep a redirection here in case this link is still used in mail
    {
      path: 'justificatifs',
      element: <Navigate to="/remboursements" replace />,
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
