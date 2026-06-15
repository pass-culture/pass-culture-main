import { withUserPermissions } from '@/commons/auth/withUserPermissions'
import { VenuePageLayout } from '@/layouts/VenuePageLayout/VenuePageLayouts'

import type { CustomRouteGroup } from '../types'
import { mustBeOnboardedWithSelectedPartnerVenue } from '../utils'

export const venuePageRouteSubgroup: CustomRouteGroup = {
  path: '/partenaire',
  loader: withUserPermissions(mustBeOnboardedWithSelectedPartnerVenue),
  Component: VenuePageLayout,
  children: [
    {
      path: 'page-partenaire',
      lazy: () => import('@/pages/IndividualVenuePage/IndividualVenuePage'),
      handle: {
        title: 'Page sur l’application',
      },
    },
  ],
}
