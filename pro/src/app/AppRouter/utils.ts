import type { UserPermissions } from '@/commons/auth/types'

export const mustBeAuthenticated = (userPermissions: UserPermissions) =>
  userPermissions.isAuthenticated

export const mustBeUnauthenticated = (userPermissions: UserPermissions) =>
  !userPermissions.isAuthenticated

export const mustHaveSelectedVenue = (userPermissions: UserPermissions) =>
  userPermissions.isAuthenticated &&
  userPermissions.isOnboarded &&
  userPermissions.isSelectedOffererAssociated

export const mustOnboard = (userPermissions: UserPermissions) =>
  userPermissions.isAuthenticated &&
  userPermissions.hasSelectedVenue &&
  !userPermissions.isOnboarded
