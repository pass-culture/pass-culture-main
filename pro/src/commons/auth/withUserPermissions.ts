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
    const hasVenues = state.user.venues && state.user.venues.length > 0

    if (!requireUserPermissions(userPermissions)) {
      switch (true) {
        case !userPermissions.isAuthenticated:
          return redirect('/connexion')

        case !hasVenues:
          return redirect('inscription/structure/recherche')

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
