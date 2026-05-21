import { withUserPermissions } from '@/commons/auth/withUserPermissions'
import { PartnerLayout } from '@/layouts/PartnerLayout/PartnerLayout'

import type { CustomRouteGroup } from '../types'
import { mustBeOnboardedWithSelectedPartnerVenue } from '../utils'

export const partnerRouteGroup: CustomRouteGroup = {
  path: '',
  loader: withUserPermissions(mustBeOnboardedWithSelectedPartnerVenue),
  Component: PartnerLayout,
  children: [
    {
      path: 'accueil',
      lazy: () => import('@/pages/Homepage/NewHomepage'),
      handle: {
        title: 'Espace acteurs culturels',
      },
    },

    {
      lazy: () => import('@/pages/Desk/Desk'),
      loader: withUserPermissions(mustBeOnboardedWithSelectedPartnerVenue),
      path: '/guichet',
      handle: {
        title: 'Guichet',
      },
    },

    // -------------------------------------------------------------------------
    // Individual

    {
      path: 'offres',
      lazy: () => import('@/pages/IndividualOffers/IndividualOffers'),
      handle: {
        title: 'Offres individuelles',
      },
    },
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
