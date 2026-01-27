import type { UserPermissions } from '@/commons/auth/types'
import { isFeatureActive } from '@/commons/store/features/selectors'
import { rootStore } from '@/commons/store/store'

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

export const hasNewHomepage = () => {
  const state = rootStore.getState()
  return (
    isFeatureActive(state, 'WIP_SWITCH_VENUE') &&
    isFeatureActive(state, 'WIP_ENABLE_NEW_PRO_HOME')
  )
}
