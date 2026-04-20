import type { UserPermissions } from '@/commons/auth/types'
import { isFeatureActive } from '@/commons/store/features/selectors'
import { rootStore } from '@/commons/store/store'

export const mustBeAuthenticated = (userPermissions: UserPermissions) =>
  userPermissions.isAuthenticated

export const mustBeUnauthenticated = (userPermissions: UserPermissions) =>
  !userPermissions.isAuthenticated

export const mustBeOnboardedWithSelectedPartnerVenue = (
  userPermissions: UserPermissions
) =>
  mustHaveSelectedPartnerVenue(userPermissions) && userPermissions.isOnboarded

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
) => userPermissions.isAuthenticated && !userPermissions.isOnboarded

export const isNewHomepageEnabled = () => {
  const state = rootStore.getState()
  return isFeatureActive(state, 'WIP_ENABLE_NEW_PRO_HOME')
}
