/* No need to test this file */
/* istanbul ignore file */

import { RouteConfig } from 'app/AppRouter/routesMap'

export const routesVenueEdition: RouteConfig[] = [
  {
    path: '/structures/:offererId/lieux/:venueId',
    title: 'Modifier un lieu',
  },
  {
    path: '/structures/:offererId/lieux/:venueId/eac',
    title: 'Modifier les informations pour les enseignants d’un lieu',
  },
]
