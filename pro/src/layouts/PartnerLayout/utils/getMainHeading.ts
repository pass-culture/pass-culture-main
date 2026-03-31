import type { UIMatch } from 'react-router'

import type { GetVenueResponseModel } from '@/apiClient/v1'
import type { CustomRouteHandle } from '@/app/AppRouter/types'
import { isNewHomepageEnabled } from '@/app/AppRouter/utils'

import { PARTNER_HEADING_OVERRIDES } from '../commons/constants'

// TODO (cmoinier): remove null typing once WIP_SWITCH_VENUE is enabled and selectedPartnerVenue is always defined
export function getMainHeading(
  currentRoute: UIMatch<unknown, CustomRouteHandle | undefined>,
  selectedPartnerVenue: GetVenueResponseModel | null
) {
  if (currentRoute.pathname === '/accueil' && isNewHomepageEnabled()) {
    return `Votre espace ${selectedPartnerVenue?.publicName}`
  }

  return PARTNER_HEADING_OVERRIDES[currentRoute.pathname]
}
