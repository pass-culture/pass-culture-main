import { getCurrentUserPermissions } from '@/commons/auth/getCurrentUserPermissions'
import { rootStore } from '@/commons/store/store'

export const getUserDefaultPath = () => {
  const userPermissions = getCurrentUserPermissions(rootStore.getState().user)

  switch (true) {
    case !userPermissions.isAuthenticated:
      return '/connexion'

    case !userPermissions.hasVenues:
      return '/inscription/structure/recherche'

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
