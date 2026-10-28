/* No need to test this file */
/* istanbul ignore file */

import { redirect } from 'react-router'

import { withUserPermissions } from '@/commons/auth/withUserPermissions'

import type { CustomRouteGroup } from './types'
import { mustBeOnboardedWithSelectedPartnerVenue } from './utils'

export const routesIndividualOfferV2: CustomRouteGroup['children'] = [
  {
    index: true,
    loader: () => redirect('creation/nature-format-domaine'),
  },
  {
    lazy: () =>
      import(
        '@/pages/IndividualOfferV2/IndividualOfferV2NatureFormatDomain/IndividualOfferV2NatureFormatDomain'
      ),
    path: 'creation/nature-format-domaine',
    handle: {
      title: 'Créer une offre - Choix du format, de la nature et du domaine',
    },
    loader: withUserPermissions(mustBeOnboardedWithSelectedPartnerVenue),
  },
  {
    lazy: () =>
      import(
        '@/pages/IndividualOfferV2/IndividualOfferV2Description/IndividualOfferV2Description'
      ),
    path: 'creation/description',
    handle: {
      title: 'Créer une offre - Description',
    },
    loader: withUserPermissions(mustBeOnboardedWithSelectedPartnerVenue),
  },
]
