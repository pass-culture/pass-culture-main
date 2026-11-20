import { withUserPermissions } from '@/commons/auth/withUserPermissions'
import { CollectiveVenuePageLayout } from '@/layouts/CollectiveVenuePageLayout/CollectiveVenuePageLayout'

import type { CustomRouteGroup } from '../types'

export const PARTENAIRE_ROUTES = {
  PARTENAIRE_COLLECTIF: '/partenaire/page-collective',
  PARTENAIRE_COLLECTIF_EDITION: '/partenaire/page-collective/edition',
  PARTENAIRE_INDIVIDUEL: '/partenaire/page-partenaire',
  PARTENAIRE_INDIVIDUEL_EDITION: '/partenaire/page-partenaire/edition',
} as const

export const partenaireRoutes: CustomRouteGroup['children'] = [
  {
    path: 'page-collective',
    Component: CollectiveVenuePageLayout,
    children: [
      {
        index: true,
        lazy: () => import('@/pages/CollectiveVenuePage/CollectiveVenuePage'),
        handle: {
          title: 'Page dans ADAGE',
        },
      },
      {
        path: 'edition',
        loader: withUserPermissions(
          (userPermissions) =>
            userPermissions.isSelectedPartnerVenueAndOffererActive
        ),
        lazy: () =>
          import(
            '@/pages/CollectiveVenuePageEdition/CollectiveVenuePageEdition'
          ),
        handle: {
          title: 'Gérer ma page sur l’application',
        },
      },
    ],
  },
  {
    path: 'page-partenaire',
    children: [
      {
        index: true,
        lazy: () => import('@/pages/IndividualVenuePage/IndividualVenuePage'),
        handle: {
          title: 'Page sur l’application',
        },
      },
      {
        path: 'edition',
        loader: withUserPermissions(
          (userPermissions) =>
            userPermissions.isSelectedPartnerVenueAndOffererActive
        ),
        lazy: () =>
          import(
            '@/pages/IndividualVenuePageEdition/IndividualVenuePageEdition'
          ),
        handle: {
          title: 'Gérer ma page sur l’application',
        },
      },
    ],
  },
]
