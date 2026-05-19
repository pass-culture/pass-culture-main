import { getCurrentUserPermissions } from '@/commons/auth/getCurrentUserPermissions'

export const getUserDefaultPath = () => {
  const userPermissions = getCurrentUserPermissions()

  switch (true) {
    case !userPermissions.isAuthenticated:
      return '/connexion'

    case !userPermissions.hasVenues:
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
