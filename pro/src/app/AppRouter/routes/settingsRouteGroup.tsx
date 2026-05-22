import { Navigate } from 'react-router'

import { withUserPermissions } from '@/commons/auth/withUserPermissions'
import { VenueSettings } from '@/pages/VenueSettings/VenueSettings'

import type { CustomRouteGroup } from '../types'
import { mustHaveSelectedPartnerVenue } from '../utils'

export const settingsRouteGroup: CustomRouteGroup = {
  path: '/parametres',
  loader: withUserPermissions(mustHaveSelectedPartnerVenue),
  handle: {
    title: 'Paramètres',
  },
  Component: VenueSettings,
  children: [
    {
      index: true,
      Component: () => <Navigate to="informations-generales" replace />,
    },
    {
      path: 'informations-generales',
      lazy: () =>
        import('@/pages/VenueSettings/GeneralInformation/GeneralInformation'),
      handle: {
        title: 'Informations générales',
      },
    },
    {
      path: 'notifications',
      lazy: () => import('@/pages/VenueSettings/Notifications/Notifications'),
      handle: {
        title: 'Notifications',
      },
    },
    {
      path: 'synchronisations',
      lazy: () =>
        import(
          '@/pages/VenueSettings/SynchronizationProviders/SynchronizationProviders'
        ),
      handle: {
        title: 'Synchronisations',
      },
    },
  ],
}
