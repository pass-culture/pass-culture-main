import { withUserPermissions } from '@/commons/auth/withUserPermissions'

import type { CustomRouteGroup } from '../types'
import { mustBeOnboardedWithSelectedPartnerVenue } from '../utils'

export const venuePageRouteSubgroup: CustomRouteGroup = {
  path: '/partenaire',
  loader: withUserPermissions(mustBeOnboardedWithSelectedPartnerVenue),
  lazy: () => import('@/layouts/VenuePageLayout/VenuePageLayout'),
  children: [
    {
      path: 'page-collective',
      lazy: () =>
        import('@/layouts/CollectiveVenuePageLayout/CollectiveVenuePageLayout'),
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
  ],
}
