import { type LoaderFunctionArgs, redirect } from 'react-router'

import { isFeatureActive } from '@/commons/store/features/selectors'
import { rootStore } from '@/commons/store/store'

import { getCurrentUserPermissions } from './getCurrentUserPermissions'
import type { UserPermissions } from './types'

export const withUserPermissions = (
  requireUserPermissions: (userPermissions: UserPermissions) => boolean,
  loader?: (args: LoaderFunctionArgs) => unknown
) => {
  return (args: LoaderFunctionArgs) => {
    const state = rootStore.getState()

    if (!isFeatureActive(state, 'WIP_SWITCH_VENUE')) {
      return loader?.(args) ?? null
    }

    const userPermissions = getCurrentUserPermissions()

    if (!requireUserPermissions(userPermissions)) {
      switch (true) {
        case !userPermissions.isAuthenticated:
          return redirect('/connexion')

        case !userPermissions.hasSelectedVenue:
          return redirect('/hub')

        case !userPermissions.isSelectedVenueAssociated:
          return redirect('/rattachement-en-cours')

        case !userPermissions.isOnboarded:
          return redirect('/onboarding')

        default:
          return redirect('/accueil')
      }
    }

    return loader?.(args) ?? null
  }
}
