import type { UserPermissions } from '@/commons/auth/types'
import { COOKIES } from '@/commons/utils/localStorageManager'

export const mustBeAuthenticated = (userPermissions: UserPermissions) =>
  userPermissions.isAuthenticated

export const mustBeUnauthenticated = (userPermissions: UserPermissions) =>
  !userPermissions.isAuthenticated

export const mustBeOnboardedOrSkipped = (userPermissions: UserPermissions) =>
  userPermissions.isSelectedPartnerVenueOnboarded ||
  document.cookie.includes(COOKIES.DID_SKIP_ONBOARDING)

export const mustBeOnboardedWithSelectedPartnerVenue = (
  userPermissions: UserPermissions
) =>
  mustHaveSelectedPartnerVenue(userPermissions) &&
  mustBeOnboardedOrSkipped(userPermissions)

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
  !userPermissions.isSelectedPartnerVenueOnboarded
