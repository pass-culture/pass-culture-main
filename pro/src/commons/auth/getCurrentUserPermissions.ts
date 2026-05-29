import type { UserSliceState } from '../store/user/reducer'
import type { UserPermissions } from './types'

/**
 * /!\ If you need to get the current user permissions within React lifecyle (components),
 * DO NOT use this function directly. Use the `useCurrentUserPermissions` hook instead
 * to ensure the permissions are refreshed on every user state update.
 */
export const getCurrentUserPermissions = (
  userSliceState: UserSliceState
): UserPermissions => {
  const {
    currentUser,
    offererNames,
    selectedAdminOfferer,
    selectedPartnerVenue,
    venues,
    venuesWithPendingValidation,
  } = userSliceState

  if (!currentUser) {
    return {
      hasSelectedPartnerVenue: false,
      hasSelectedAdminOfferer: false,
      hasVenues: false,
      isAuthenticated: false,
      isSelectedAdminOffererAssociated: false,
      isSelectedPartnerVenueAssociated: false,
      isSelectedPartnerVenueOnboarded: false,
    }
  }

  const hasSelectedAdminOfferer = !!selectedAdminOfferer
  const hasSelectedPartnerVenue = !!selectedPartnerVenue
  const isSelectedAdminOffererAssociated =
    hasSelectedAdminOfferer &&
    !!offererNames?.some(
      (offerer) => offerer.validated && offerer.id === selectedAdminOfferer.id
    )
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
    isSelectedAdminOffererAssociated,
    isSelectedPartnerVenueAssociated,
    isSelectedPartnerVenueOnboarded: !!selectedPartnerVenue?.isOnboarded,
  }
}
