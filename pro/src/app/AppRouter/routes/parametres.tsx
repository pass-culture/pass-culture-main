import { Navigate } from 'react-router'

export const PARAMETRES_ROUTES = {
  PARAMETRES: '/parametres',
  PARAMETRES_GENERAL: '/parametres/informations-generales',
  PARAMETRES_NOTIFICATIONS: '/parametres/notifications',
  PARAMETRES_SYNCHRONIZATION: '/parametres/synchronisations',
  PARAMETRES_GESTION: '/parametres/gestion-structure',
} as const

export const parametresRoutes = [
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
  {
    path: 'gestion-structure',
    lazy: () => import('@/pages/VenueSettings/VenueManagement/VenueManagement'),
    handle: {
      title: 'Gestion de la structure',
    },
    featureName: 'WIP_CLOSE_VENUE',
  },
]
