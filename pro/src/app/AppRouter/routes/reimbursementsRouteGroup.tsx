import { Navigate, useLocation } from 'react-router'

import type { CustomRouteGroup } from '../types'

export const reimbursementsRouteGroup: CustomRouteGroup['children'] = [
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
      title: 'Gestion financière',
      mainTitle: 'Gestion financière',
    },
    featureName: 'WIP_ENABLE_FINANCE_SETTLEMENTS',
  },
  {
    path: 'informations-bancaires',
    lazy: () =>
      import('@/pages/Reimbursements/BankInformations/BankInformations'),
    handle: {
      title: 'Informations bancaires',
      mainTitle: 'Gestion financière',
    },
  },
  {
    path: 'chiffre-d-affaires',
    lazy: () => import('@/pages/Reimbursements/Income/Income'),
    handle: {
      title: 'Chiffre d’affaires',
      mainTitle: 'Gestion financière',
    },
  },
]
