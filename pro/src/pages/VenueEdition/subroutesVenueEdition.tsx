/* No need to test this file */
/* istanbul ignore file */

import { RouteConfig } from 'app/AppRouter/routesMap'

export const routesVenueEdition: RouteConfig[] = [
  {
    path: '/structures/:offererId/lieux/:venueId',
    title: 'Gérer ma page sur l’application',
  },
  {
    path: '/structures/:offererId/lieux/:venueId/edition',
    title: 'Gérer ma page sur l’application',
  },
  {
    path: '/structures/:offererId/lieux/:venueId/collectif',
    title: 'Gérer ma page sur ADAGE',
  },
]
