import { getCurrentUserPermissions } from '@/commons/auth/getCurrentUserPermissions'
import { rootStore } from '@/commons/store/store'

export const getUserDefaultPath = () => {
  const state = rootStore.getState()

  const userPermissions = getCurrentUserPermissions()
  const hasVenues = state.user.venues && state.user.venues.length > 0

  switch (true) {
    case !userPermissions.isAuthenticated:
      return '/connexion'

    case !hasVenues:
      return '/inscription/structure/recherche'

    case !userPermissions.hasSelectedPartnerVenue:
      return '/hub'

    case !userPermissions.isSelectedPartnerVenueAssociated:
      return '/rattachement-en-cours'

    case !userPermissions.isOnboarded:
      return '/onboarding'

    default:
      return '/accueil'
  }
}
