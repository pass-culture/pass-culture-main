import type { UserPermissions } from '@/commons/auth/types'

export const mustBeAuthenticated = (userPermissions: UserPermissions) =>
  userPermissions.isAuthenticated

export const mustBeUnauthenticated = (userPermissions: UserPermissions) =>
  !userPermissions.isAuthenticated

export const mustHaveAnAssociatedSelectedVenue = (
  userPermissions: UserPermissions
) => userPermissions.isSelectedVenueAssociated

export const mustNotBeOnboarded = (userPermissions: UserPermissions) =>
  !userPermissions.isOnboarded

export const isPermissionless = () => true
