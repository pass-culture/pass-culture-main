import type { UserPermissions } from '@/commons/auth/types'
import { isFeatureActive } from '@/commons/store/features/selectors'
import { rootStore } from '@/commons/store/store'

export const mustBeAuthenticated = (userPermissions: UserPermissions) =>
  userPermissions.isAuthenticated

export const mustBeUnauthenticated = (userPermissions: UserPermissions) =>
  !userPermissions.isAuthenticated

export const mustOnboardedWithSelectedVenue = (
  userPermissions: UserPermissions
) => mustHaveSelectedVenue(userPermissions) && userPermissions.isOnboarded

export const mustHaveSelectedVenue = (userPermissions: UserPermissions) =>
  userPermissions.isAuthenticated && userPermissions.isSelectedVenueAssociated

export const mustHaveSelectedAdminOfferer = (
  userPermissions: UserPermissions
) => userPermissions.isAuthenticated && userPermissions.hasSelectedAdminOfferer

export const mustNotBeOnboarded = (userPermissions: UserPermissions) =>
  userPermissions.isAuthenticated && !userPermissions.isOnboarded

export const isNewHomepageEnabled = () => {
  const state = rootStore.getState()
  return (
    isSwitchVenueEnabled() && isFeatureActive(state, 'WIP_ENABLE_NEW_PRO_HOME')
  )
}

export const isSwitchVenueEnabled = () => {
  const state = rootStore.getState()
  return isFeatureActive(state, 'WIP_SWITCH_VENUE')
}
