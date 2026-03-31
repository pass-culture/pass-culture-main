import { rootStore } from '@/commons/store/store'

import type { UserPermissions } from './types'

export const getCurrentUserPermissions = (): UserPermissions => {
  const { access, currentUser, selectedAdminOfferer, selectedPartnerVenue } =
    rootStore.getState().user

  if (!currentUser) {
    return {
      hasSelectedPartnerVenue: false,
      isAuthenticated: false,
      isOnboarded: false,
      isSelectedPartnerVenueAssociated: false,
      hasSelectedAdminOfferer: false,
    }
  }

  const hasSelectedAdminOfferer = !!selectedAdminOfferer
  const hasSelectedPartnerVenue = !!selectedPartnerVenue
  // TODO (igabriele, 2026-02-04): Replace `access !== 'unattached'` with `selectedPartnerVenue.isAssociated` as soon as the prop is available (WIP_SWITCH_VENUE FF).
  const isSelectedPartnerVenueAssociated =
    hasSelectedPartnerVenue && access !== 'unattached'
  // TODO (igabriele, 2026-02-04): Replace `access !== 'no-onboarding'` with `selectedPartnerVenue.isOnboarded` as soon as the prop is available (WIP_SWITCH_VENUE FF).
  const isOnboarded =
    hasSelectedPartnerVenue &&
    isSelectedPartnerVenueAssociated &&
    access !== 'no-onboarding'

  return {
    hasSelectedPartnerVenue: hasSelectedPartnerVenue,
    isAuthenticated: true,
    isOnboarded,
    isSelectedPartnerVenueAssociated,
    hasSelectedAdminOfferer,
  }
}
