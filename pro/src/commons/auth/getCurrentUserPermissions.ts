import { rootStore } from '@/commons/store/store'

import type { UserPermissions } from './types'

export const getCurrentUserPermissions = (): UserPermissions => {
  const { access, currentUser, selectedVenue } = rootStore.getState().user
  const { offererNames } = rootStore.getState().offerer

  if (!currentUser) {
    return {
      hasSelectedVenue: false,
      hasSomeOfferer: false,
      isAuthenticated: false,
      isOnboarded: false,
      isSelectedOffererAssociated: false,
    }
  }

  const hasSomeOfferer = (offererNames ?? []).length > 0
  const hasSelectedVenue = !!selectedVenue
  const isSelectedVenueAssociated = access !== 'unattached'
  const isOnboarded =
    hasSelectedVenue && isSelectedVenueAssociated && access !== 'no-onboarding'

  return {
    hasSelectedVenue,
    hasSomeOfferer: hasSomeOfferer,
    isAuthenticated: true,
    isOnboarded,
    isSelectedOffererAssociated: isSelectedVenueAssociated,
  }
}
