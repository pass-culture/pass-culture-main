import { withUserPermissions } from '@/commons/auth/withUserPermissions'
import { PartnerLayout } from '@/layouts/PartnerLayout/PartnerLayout'

import type { CustomRouteGroup } from '../types'
import { isNewHomepageEnabled, mustOnboardedWithSelectedVenue } from '../utils'

export const partnerRouteGroup: CustomRouteGroup = {
  path: '',
  loader: withUserPermissions(mustOnboardedWithSelectedVenue),
  Component: PartnerLayout,
  children: [
    {
      path: 'accueil',
      lazy: () =>
        isNewHomepageEnabled()
          ? import('@/pages/Homepage/NewHomepage')
          : import('@/pages/Homepage/Homepage'),
      handle: {
        title: 'Espace acteurs culturels',
      },
    },

    // -------------------------------------------------------------------------
    // Individual

    {
      path: 'reservations',
      handle: {
        title: 'Réservations individuelles',
      },
      lazy: () => import('@/pages/IndividualBookings/IndividualBookings'),
    },

    // -------------------------------------------------------------------------
    // Collective

    {
      path: 'offres/collectives',
      handle: {
        title: 'Offres collectives',
      },
      lazy: () => import('@/pages/CollectiveOffers/CollectiveOffers'),
    },
  ],
}
