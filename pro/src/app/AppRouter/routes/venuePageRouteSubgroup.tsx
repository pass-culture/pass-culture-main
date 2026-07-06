import { withUserPermissions } from '@/commons/auth/withUserPermissions'
import { CollectiveVenuePageLayout } from '@/layouts/CollectiveVenuePageLayout/CollectiveVenuePageLayout'
import { VenuePageLayout } from '@/layouts/VenuePageLayout/VenuePageLayout'

import type { CustomRouteGroup } from '../types'
import { mustBeOnboardedWithSelectedPartnerVenue } from '../utils'

export const venuePageRouteSubgroup: CustomRouteGroup = {
  path: '/partenaire',
  loader: withUserPermissions(mustBeOnboardedWithSelectedPartnerVenue),
  Component: VenuePageLayout,
  children: [
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
      handle: {
        title: 'Page sur lapplication',
      },
      children: [
        {
          index: true,
          lazy: () => import('@/pages/IndividualVenuePage/IndividualVenuePage'),
        },
        {
          path: 'edition',
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
  ],
}
