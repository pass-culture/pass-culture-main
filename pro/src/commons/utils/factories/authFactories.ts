import type { UserPermissions } from '@/commons/auth/types'

export const makeUserPermissions = (
  overrides: Partial<UserPermissions>
): UserPermissions => ({
  hasSelectedAdminOfferer: false,
  hasSelectedPartnerVenue: false,
  hasVenues: false,
  isAuthenticated: false,
  isSelectedPartnerVenueActive: false,
  isSelectedAdminOffererAssociated: false,
  isSelectedPartnerVenueAssociated: false,
  isSelectedPartnerVenueOnboarded: false,
  ...overrides,
})
