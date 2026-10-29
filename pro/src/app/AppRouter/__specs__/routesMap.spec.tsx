import { screen, waitFor } from '@testing-library/react'
import { matchRoutes, useLocation } from 'react-router'

import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { NavigateToNewPasswordReset, routes } from '../routesMap'

const CurrentPath = () => {
  const { pathname } = useLocation()

  return <span data-testid="current-path">{pathname}</span>
}

describe('NavigateToNewPasswordReset', () => {
  it('should redirect to the password reset page with the token from query params', async () => {
    renderWithProviders(null, {
      initialRouterEntries: ['/mot-de-passe-perdu?token=token-123'],
      routes: [
        {
          element: <NavigateToNewPasswordReset to="/demande-mot-de-passe" />,
          path: '/mot-de-passe-perdu',
        },
        {
          element: <CurrentPath />,
          path: '/demande-mot-de-passe/:token',
        },
      ],
    })

    await waitFor(() => {
      expect(screen.getByTestId('current-path')).toHaveTextContent(
        '/demande-mot-de-passe/token-123'
      )
    })
  })

  it('should support location object destinations', async () => {
    renderWithProviders(null, {
      initialRouterEntries: ['/mot-de-passe-perdu?token=token-456'],
      routes: [
        {
          element: (
            <NavigateToNewPasswordReset
              to={{ pathname: '/demande-mot-de-passe' }}
            />
          ),
          path: '/mot-de-passe-perdu',
        },
        {
          element: <CurrentPath />,
          path: '/demande-mot-de-passe/:token',
        },
      ],
    })

    await waitFor(() => {
      expect(screen.getByTestId('current-path')).toHaveTextContent(
        '/demande-mot-de-passe/token-456'
      )
    })
  })
})

describe('routesMap', () => {
  it.each([
    '/',
    '/administration',
    '/administration/gestion-financiere',
    '/administration/gestion-financiere/justificatifs',
    '/administration/gestion-financiere/virements',
    '/administration/gestion-financiere/informations-bancaires',
    '/administration/gestion-financiere/chiffre-d-affaires',
    '/administration/collaborateurs',
    '/administration/donnees-activite/individuel',
    '/administration/donnees-activite/collectif',
    '/accueil',
    '/guichet',
    '/offres',
    '/reservations',
    '/offres/collectives',
    '/partenaire',
    '/partenaire/page-collective',
    '/partenaire/page-collective/edition',
    '/partenaire/page-partenaire',
    '/partenaire/page-partenaire/edition',
    '/parametres',
    '/parametres/informations-generales',
    '/parametres/notifications',
    '/parametres/synchronisations',
    '/parametres/gestion-structure',
    '/hub',
    '/adage-iframe/*',
    '/adage-iframe/*/*',
    '/adage-iframe/erreur',
    '/inscription',
    '/inscription/compte/creation',
    '/inscription/compte/confirmation',
    '/inscription/compte/confirmation/:token',
    '/inscription/validation/:token',
    '/inscription/confirmation',
    '/erreur/indisponible',
    '/connexion',
    '/email_validation',
    '/structures/lieux/creation',
    '/offre/creation',
    '/offres/vitrines',
    '/offre/creation/collectif/selection',
    '/offre/:offerId/collectif/stocks',
    '/offre/:offerId/collectif/informations-pratiques',
    '/offre/creation/collectif',
    '/offre/creation/collectif/vitrine',
    '/offre/collectif/:offerId/creation',
    '/offre/collectif/vitrine/:offerId/creation',
    '/offre/:offerId/collectif/etablissement',
    '/offre/:offerId/collectif/creation/recapitulatif',
    '/offre/:offerId/collectif/creation/apercu',
    '/offre/:offerId/collectif/vitrine/creation/apercu',
    '/offre/:offerId/collectif/vitrine/creation/recapitulatif',
    '/offre/:offerId/collectif/confirmation',
    '/offre/:offerId/collectif/vitrine/confirmation',
    '/offre/:offerId/collectif/edition',
    '/offre/:offerId/collectif/recapitulatif',
    '/offre/:offerId/collectif/vitrine/apercu',
    '/offre/:offerId/collectif/apercu',
    '/offre/:offerId/collectif/stocks/edition',
    '/offre/:offerId/collectif/informations-pratiques/edition',
    '/offre/:offerId/collectif/etablissement/edition',
    '/offre/collectif/creation/:offerId/requete/:requestId',
    '/demande-mot-de-passe/:token',
    '/mot-de-passe-perdu',
    '/demande-mot-de-passe',
    '/offre/individuelle',
    '/offre/individuelle/:offerId/edition/details',
    '/offre/individuelle/:offerId/visibilite',
    '/offre/individuelle/creation/description',
    '/offre/individuelle/:offerId/creation/description',
    '/offre/individuelle/:offerId/edition/description',
    '/offre/individuelle/:offerId/creation/pratiques',
    '/offre/individuelle/:offerId/edition/pratiques',
    '/offre/individuelle/:offerId/creation/localisation',
    '/offre/individuelle/:offerId/edition/localisation',
    '/offre/individuelle/:offerId/creation/media',
    '/offre/individuelle/:offerId/edition/media',
    '/offre/individuelle/:offerId/creation/tarifs',
    '/offre/individuelle/:offerId/edition/tarifs',
    '/offre/individuelle/:offerId/creation/horaires',
    '/offre/individuelle/:offerId/edition/horaires',
    '/offre/individuelle/:offerId/creation/informations_pratiques',
    '/offre/individuelle/:offerId/edition/informations_pratiques',
    '/offre/individuelle/:offerId/reservations',
    '/offre/individuelle/:offerId/creation/confirmation',
    '/offre/individuelle/:offerId/creation/recapitulatif',
    '/onboarding/offre/individuelle',
    '/onboarding/offre/individuelle/creation/description',
    '/onboarding/offre/individuelle/:offerId/creation/description',
    '/onboarding/offre/individuelle/:offerId/creation/pratiques',
    '/onboarding/offre/individuelle/:offerId/creation/localisation',
    '/onboarding/offre/individuelle/:offerId/creation/media',
    '/onboarding/offre/individuelle/:offerId/creation/tarifs',
    '/onboarding/offre/individuelle/:offerId/creation/informations_pratiques',
    '/onboarding/offre/individuelle/:offerId/creation/stocks',
    '/onboarding/offre/individuelle/:offerId/creation/horaires',
    '/onboarding/offre/individuelle/:offerId/creation/recapitulatif',
    '/profil',
    '/inscription/structure',
    '/inscription/structure/recherche',
    '/inscription/structure/rattachement',
    '/inscription/structure/rattachement/confirmation-rattachement',
    '/inscription/structure/identification',
    '/inscription/structure/activite',
    '/inscription/structure/confirmation',
    '/plan-du-site',
    '/accessibilite',
    '/accessibilite/engagements',
    '/accessibilite/declaration',
    '/ecoconception',
    '/ecoconception/politique',
    '/ecoconception/declaration',
    '/onboarding',
    '/onboarding/individuel',
    '/bienvenue',
    '/bienvenue/publics',
    '/bienvenue/offres-jeunes',
    '/bienvenue/offres-scolaires',
    '/bienvenue/avantages',
    '/bienvenue/prochaines-etapes',
    '/inscription/preparation',
    '/inscription/preparation/siret',
    '/inscription/preparation/accueil-public',
    '/inscription/preparation/activite',
    '/inscription/preparation/publics',
    '/inscription/preparation/resultats',
    '/inscription/preparation/email',
    '/inscription/preparation/email-confirmation',
    '/404',
    '/rattachement-en-cours',
  ])('should have the path %s', (path) => {
    expect(matchRoutes(routes, path)).not.toBeNull()
  })
})
