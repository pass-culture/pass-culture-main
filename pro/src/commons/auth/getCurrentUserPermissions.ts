import { rootStore } from '@/commons/store/store'

import type { UserPermissions } from './types'

export const getCurrentUserPermissions = (): UserPermissions => {
  const { access, currentUser, selectedAdminOfferer, selectedVenue } =
    rootStore.getState().user

  if (!currentUser) {
    return {
      hasSelectedVenue: false,
      isAuthenticated: false,
      isOnboarded: false,
      isSelectedVenueAssociated: false,
      hasSelectedAdminOfferer: false,
    }
  }

  const hasSelectedAdminOfferer = !!selectedAdminOfferer
  const hasSelectedVenue = !!selectedVenue
  // TODO (igabriele, 2026-02-04): Replace `access !== 'unattached'` with `selectedVenue.isAssociated` as soon as the prop is available.
  const isSelectedVenueAssociated = hasSelectedVenue && access !== 'unattached'
  // TODO (igabriele, 2026-02-04): Replace `access !== 'no-onboarding'` with `selectedVenue.isOnboarded` as soon as the prop is available.
  const isOnboarded =
    hasSelectedVenue && isSelectedVenueAssociated && access !== 'no-onboarding'

  return {
    hasSelectedVenue,
    isAuthenticated: true,
    isOnboarded,
    isSelectedVenueAssociated,
    hasSelectedAdminOfferer,
  }
}
