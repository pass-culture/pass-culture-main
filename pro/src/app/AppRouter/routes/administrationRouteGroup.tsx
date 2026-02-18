import { withUserPermissions } from '@/commons/auth/withUserPermissions'
import { AdministrationLayout } from '@/layouts/AdministrationLayout/AdministrationLayout'

import type { CustomRouteGroup } from '../types'
import { mustHaveSelectedAdminOfferer } from '../utils'

export const administrationRouteGroup: CustomRouteGroup = {
  path: '/administration',
  loader: withUserPermissions(mustHaveSelectedAdminOfferer),
  Component: AdministrationLayout,
  children: [
    {
      path: 'donnees-activite/individuel',
      handle: {
        title: "Données d'activité : individuel",
      },
      lazy: () =>
        import('@/pages/IndividualActivityData/IndividualActivityData'),
    },
    {
      path: 'donnees-activite/collectif',
      handle: {
        title: "Données d'activité : collectif",
      },
      lazy: () =>
        import('@/pages/CollectiveActivityData/CollectiveActivityData'),
    },
  ],
}
