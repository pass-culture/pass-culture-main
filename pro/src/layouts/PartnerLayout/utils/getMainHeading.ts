import type { UIMatch } from 'react-router'

import type { GetVenueResponseModel } from '@/apiClient/v1'
import type { CustomRouteHandle } from '@/app/AppRouter/types'
import { isNewHomepageEnabled } from '@/app/AppRouter/utils'

import { PARTNER_HEADING_OVERRIDES } from '../commons/constants'

export function getMainHeading(
  currentRoute: UIMatch<unknown, CustomRouteHandle | undefined>,
  selectedPartnerVenue: GetVenueResponseModel
) {
  if (currentRoute.pathname === '/accueil' && isNewHomepageEnabled()) {
    return `Votre espace ${selectedPartnerVenue.publicName}`
  }

  return PARTNER_HEADING_OVERRIDES[currentRoute.pathname]
}
