import { Navigate, useLocation } from 'react-router'

import type { CustomRouteGroup } from '../types'

export const ADMIN_REIMBURSEMENT = {
  ADMIN_REIMBURSEMENT_INDEX: '/administration/gestion-financiere',
  ADMIN_REIMBURSEMENT_JUSTIFICATIFS:
    '/administration/gestion-financiere/justificatifs',
  ADMIN_REIMBURSEMENT_VIREMENTS: '/administration/gestion-financiere/virements',
  ADMIN_REIMBURSEMENT_BANKINFOS:
    '/administration/gestion-financiere/informations-bancaires',
  ADMIN_REIMBURSEMENT_INCOME:
    '/administration/gestion-financiere/chiffre-d-affaires',
} as const

export const administrationReimbursementsRoutes: CustomRouteGroup['children'] =
  [
    {
      index: true,
      handle: {
        title: 'Gestion financière',
        mainTitle: 'Gestion financière',
      },
      Component: () => {
        const location = useLocation()
        const targetUrl = `/administration/gestion-financiere/justificatifs${location.search}`
        return <Navigate to={targetUrl} replace />
      },
    },
    {
      path: 'justificatifs',
      lazy: () =>
        import(
          '@/pages/Reimbursements/ReimbursementsInvoices/ReimbursementsInvoices'
        ),
      handle: {
        title: 'Gestion financière - justificatifs',
        mainTitle: 'Gestion financière',
      },
    },
    {
      path: 'virements',
      lazy: () => import('@/pages/Reimbursements/Settlements/Settlements'),
      handle: {
        title: 'Gestion financière - virements',
        mainTitle: 'Gestion financière',
      },
      featureName: 'WIP_ENABLE_FINANCE_SETTLEMENTS',
    },
    {
      path: 'informations-bancaires',
      lazy: () =>
        import('@/pages/Reimbursements/BankInformations/BankInformations'),
      handle: {
        title: 'Gestion financière - informations bancaires',
        mainTitle: 'Gestion financière',
      },
    },
    {
      path: 'chiffre-d-affaires',
      lazy: () => import('@/pages/Reimbursements/Income/Income'),
      handle: {
        title: 'Gestion financière - chiffre d’affaires',
        mainTitle: 'Gestion financière',
      },
    },
  ]
