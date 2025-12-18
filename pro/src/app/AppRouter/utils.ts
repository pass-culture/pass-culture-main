import type { UserPermissions } from '@/commons/auth/types'

export const mustBeAuthenticated = (userPermissions: UserPermissions) =>
  userPermissions.isAuthenticated

export const mustBeUnauthenticated = (userPermissions: UserPermissions) =>
  !userPermissions.isAuthenticated

export const mustHaveSelectedVenue = (userPermissions: UserPermissions) =>
  userPermissions.isAuthenticated &&
  userPermissions.isOnboarded &&
  userPermissions.isSelectedVenueAssociated

export const mustNotBeOnboarded = (userPermissions: UserPermissions) =>
  userPermissions.isAuthenticated && !userPermissions.isOnboarded
