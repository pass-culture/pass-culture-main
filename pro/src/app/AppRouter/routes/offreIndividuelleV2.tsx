/* No need to test this file */
/* istanbul ignore file */

import { redirect } from 'react-router'

import { withUserPermissions } from '@/commons/auth/withUserPermissions'

import type { CustomRouteGroup } from '../types'
import { mustBeOnboardedWithSelectedPartnerVenue } from '../utils'
import { mustHaveSelectedNatureAndFormat } from '../utils/mustHaveSelectedNatureAndFormat'

export const OFFRE_INDIVIDUELLE_V2_ROUTES = {
  OFFRE_INDIVIDUELLE_V2: '/offre/individuelle/v2',
  OFFRE_INDIVIDUELLE_V2_CREATION_NATURE_FORMAT_DOMAINE:
    '/offre/individuelle/v2/creation/nature-format-domaine',
  OFFRE_INDIVIDUELLE_V2_CREATION_DESCRIPTION:
    '/offre/individuelle/v2/creation/description',
} as const

export const offreIndividuelleV2Routes: CustomRouteGroup['children'] = [
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
    path: 'creation/description',
    lazy: () =>
      import(
        '@/pages/IndividualOfferV2/IndividualOfferV2Description/IndividualOfferV2Description'
      ),
    handle: {
      title: 'Créer une offre - Description',
    },
    loader: withUserPermissions(
      mustBeOnboardedWithSelectedPartnerVenue,
      mustHaveSelectedNatureAndFormat
    ),
  },
]
