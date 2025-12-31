import { useAppSelector } from '../hooks/useAppSelector'
import type { UserPermissions } from './types'

export const useCurrentUserPermissions = (): UserPermissions => {
  const access = useAppSelector((state) => state.user.access)
  const currentUser = useAppSelector((state) => state.user.currentUser)
  const selectedVenue = useAppSelector((state) => state.user.selectedVenue)

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
    isSelectedVenueAssociated: isSelectedVenueAssociated,
  }
}
