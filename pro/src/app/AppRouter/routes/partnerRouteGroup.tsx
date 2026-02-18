import { withUserPermissions } from '@/commons/auth/withUserPermissions'
import { PartnerLayout } from '@/layouts/PartnerLayout/PartnerLayout'

import type { CustomRouteGroup } from '../types'
import { isNewHomepageEnabled, mustHaveSelectedVenue } from '../utils'

export const partnerRouteGroup: CustomRouteGroup = {
  path: '',
  loader: withUserPermissions(mustHaveSelectedVenue),
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
      lazy: () => import('@/pages/Bookings/IndividualBookings'),
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
