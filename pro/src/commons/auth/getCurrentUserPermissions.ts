import { rootStore } from '@/commons/store/store'

import type { UserPermissions } from './types'

export const getCurrentUserPermissions = (): UserPermissions => {
  const {
    currentUser,
    selectedAdminOfferer,
    selectedPartnerVenue,
    venues,
    venuesWithPendingValidation,
  } = rootStore.getState().user

  if (!currentUser) {
    return {
      hasSelectedPartnerVenue: false,
      hasVenues: false,
      isAuthenticated: false,
      isOnboarded: false,
      isSelectedPartnerVenueAssociated: false,
      hasSelectedAdminOfferer: false,
    }
  }

  const hasSelectedAdminOfferer = !!selectedAdminOfferer
  const hasSelectedPartnerVenue = !!selectedPartnerVenue
  const isSelectedPartnerVenueAssociated =
    hasSelectedPartnerVenue &&
    !venuesWithPendingValidation?.some(
      (venue) => venue.id === selectedPartnerVenue.id
    )

  return {
    hasSelectedAdminOfferer,
    hasSelectedPartnerVenue,
    hasVenues: !!venues?.length,
    isAuthenticated: true,
    isOnboarded: !!selectedPartnerVenue?.isOnboarded,
    isSelectedPartnerVenueAssociated,
  }
}
