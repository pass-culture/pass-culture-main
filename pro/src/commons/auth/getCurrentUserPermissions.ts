import { rootStore } from '@/commons/store/store'

import type { UserPermissions } from './types'

export const getCurrentUserPermissions = (): UserPermissions => {
  const { access, currentUser, selectedVenue } = rootStore.getState().user

  if (!currentUser) {
    return {
      hasSelectedVenue: false,
      isAuthenticated: false,
      isOnboarded: false,
      isSelectedVenueAssociated: false,
    }
  }

  const hasSelectedVenue = !!selectedVenue
  const isSelectedVenueAssociated = hasSelectedVenue && access !== 'unattached'
  const isOnboarded =
    hasSelectedVenue && isSelectedVenueAssociated && access !== 'no-onboarding'

  return {
    hasSelectedVenue,
    isAuthenticated: true,
    isOnboarded,
    isSelectedVenueAssociated,
  }
}
