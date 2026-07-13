import type { UserPermissions } from '@/commons/auth/types'

export const mustBeAuthenticated = (userPermissions: UserPermissions) =>
  userPermissions.isAuthenticated

export const mustBeUnauthenticated = (userPermissions: UserPermissions) =>
  !userPermissions.isAuthenticated

export const mustBeOnboardedWithSelectedPartnerVenue = (
  userPermissions: UserPermissions
) =>
  mustHaveSelectedPartnerVenue(userPermissions) &&
  userPermissions.isSelectedPartnerVenueOnboarded

export const mustBeOnboardedWithActiveSelectedPartnerVenue = (
  userPermissions: UserPermissions
) =>
  mustBeOnboardedWithSelectedPartnerVenue(userPermissions) &&
  userPermissions.isSelectedPartnerVenueActive

export const mustHaveSelectedPartnerVenue = (
  userPermissions: UserPermissions
) =>
  userPermissions.isAuthenticated &&
  userPermissions.isSelectedPartnerVenueAssociated

export const mustHaveSelectedAdminOfferer = (
  userPermissions: UserPermissions
) => userPermissions.isAuthenticated && userPermissions.hasSelectedAdminOfferer

export const mustNotBeOnboardedWithSelectedPartnerVenue = (
  userPermissions: UserPermissions
) =>
  userPermissions.isAuthenticated &&
  !userPermissions.isSelectedPartnerVenueOnboarded &&
  userPermissions.isSelectedPartnerVenueActive
