import { getCurrentUserPermissions } from '@/commons/auth/getCurrentUserPermissions'
import { rootStore } from '@/commons/store/store'

export const getUserDefaultPath = (search: string = '') => {
  const state = rootStore.getState()
  const userPermissions = getCurrentUserPermissions(state.user)

  switch (true) {
    case !userPermissions.isAuthenticated:
      return '/connexion'

    case !userPermissions.hasVenues:
      return `/inscription/structure/recherche${search}`

    case !userPermissions.hasSelectedPartnerVenue:
      return '/hub'

    case !userPermissions.isSelectedPartnerVenueAssociated:
      return '/rattachement-en-cours'

    case !userPermissions.isSelectedPartnerVenueOnboarded:
      return '/onboarding'

    default:
      return '/accueil'
  }
}
