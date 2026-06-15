/* No need to test this file */
/* istanbul ignore file */

import { Navigate, type NavigateProps, useLocation } from 'react-router'

import { routesSimulator } from '@/app/AppRouter/subroutesSimulator'
import { routesWelcomeCarousel } from '@/app/AppRouter/subroutesWelcomeCarousel'
import { withUserPermissions } from '@/commons/auth/withUserPermissions'
import { noop } from '@/commons/utils/noop'
import { parse } from '@/commons/utils/query-string'

import { administrationRouteGroup } from './routes/administrationRouteGroup'
import { partnerRouteGroup } from './routes/partnerRouteGroup'
import { venuePageRouteSubgroup } from './routes/venuePageRouteSubgroup'
import { venueSettingsRouteSubgroup } from './routes/venueSettingsRouteSubgroup'
import { routesEcoDesign } from './subroutesEcoDesignMap'
import {
  routesIndividualOfferWizard,
  routesOnboardingIndividualOfferWizard,
} from './subroutesIndividualOfferWizardMap'
import { routesSignupJourney } from './subroutesSignupJourneyMap'
import { routesSignup } from './subroutesSignupMap'
import type { CustomRouteTree } from './types'
import {
  mustBeAuthenticated,
  mustBeOnboardedWithSelectedPartnerVenue,
  mustBeUnauthenticated,
  mustNotBeOnboardedWithSelectedPartnerVenue,
} from './utils'

const NavigateToNewPasswordReset = ({ to, ...props }: NavigateProps) => {
  const { search } = useLocation()
  const { token } = parse(search)
  return <Navigate {...props} to={`${to}/${token}`} />
}

export const routes: CustomRouteTree = [
  {
    element: <Navigate to="/connexion" />,
    loader: withUserPermissions(mustBeUnauthenticated),
    path: '/',
    handle: {
      title: 'Espace acteurs culturels',
    },
  },
  administrationRouteGroup,
  partnerRouteGroup,
  venuePageRouteSubgroup,
  venueSettingsRouteSubgroup,
  {
    lazy: () => import('@/pages/Hub/Hub'),
    loader: withUserPermissions(mustBeAuthenticated),
    path: '/hub',
    handle: {
      title: 'Changer de structure',
    },
  },
  {
    path: '/adage-iframe/*',
    loader: withUserPermissions(mustBeUnauthenticated),
    children: [
      {
        path: '*',
        loader: withUserPermissions(mustBeUnauthenticated),
        handle: {
          title: 'ADAGE',
        },
        lazy: () => import('@/pages/AdageIframe/app/App'),
      },
    ],
  },
  {
    lazy: () =>
      import(
        '@/pages/AdageIframe/app/components/UnauthenticatedError/UnauthenticatedError'
      ),
    path: '/adage-iframe/erreur',
    loader: withUserPermissions(mustBeUnauthenticated),
    handle: {
      title: 'ADAGE',
    },
  },
  {
    lazy: () => import('@/pages/Signup/Signup'),
    loader: withUserPermissions(mustBeUnauthenticated),
    path: '/inscription',
    handle: {
      title: 'Créez votre compte',
    },
    children: routesSignup,
  },
  {
    lazy: () => import('@/pages/Errors/Unavailable/Unavailable'),
    loader: noop,
    path: '/erreur/indisponible',
    handle: {
      title: 'Page indisponible',
      isErrorPage: true,
    },
  },
  {
    lazy: () => import('@/pages/SignIn/SignIn'),
    loader: withUserPermissions(mustBeUnauthenticated),
    path: '/connexion',
    handle: {
      title: 'Connectez-vous',
    },
  },
  {
    lazy: () => import('@/pages/EmailChangeValidation/EmailChangeValidation'),
    loader: noop,
    path: '/email_validation',
    handle: {
      title: 'Valider l’adresse email',
    },
  },
  {
    element: <Navigate to="/inscription/structure/recherche" />,
    loader: withUserPermissions(mustBeAuthenticated),
    path: '/structures/lieux/creation',
    handle: {
      title: 'Créer un lieu',
    },
  },
  {
    lazy: () => import('@/pages/VenueEdition/VenueEdition'),
    loader: withUserPermissions(mustBeOnboardedWithSelectedPartnerVenue),
    path: '/partenaire/page-partenaire/edition',
    handle: {
      title: 'Gérer ma page sur l’application',
    },
  },
  {
    lazy: () => import('@/pages/VenueEdition/VenueEdition'),
    loader: withUserPermissions(mustBeOnboardedWithSelectedPartnerVenue),
    path: '/partenaire/page-collective',
    handle: {
      title: 'Page dans ADAGE',
    },
    children: [
      {
        lazy: () => import('@/pages/VenueEdition/VenueEdition'),
        loader: withUserPermissions(mustBeOnboardedWithSelectedPartnerVenue),
        path: '*',
        title: 'Gérer ma page sur ADAGE',
      },
    ],
  },
  {
    lazy: () => import('@/pages/CollectiveOffer/CollectiveOfferType/OfferType'),
    loader: withUserPermissions(mustBeOnboardedWithSelectedPartnerVenue),
    path: '/offre/creation',
    handle: {
      title: 'Créer une offre collective',
    },
  },
  {
    lazy: () =>
      import('@/pages/TemplateCollectiveOffers/TemplateCollectiveOffers'),
    loader: withUserPermissions(mustBeOnboardedWithSelectedPartnerVenue),
    path: '/offres/vitrines',
    handle: {
      title: 'Offres vitrines',
    },
  },
  {
    lazy: () =>
      import(
        '@/pages/CollectiveOfferSelectionDuplication/CollectiveOfferSelectionDuplication'
      ),
    loader: withUserPermissions(mustBeOnboardedWithSelectedPartnerVenue),
    path: '/offre/creation/collectif/selection',
    handle: {
      title: 'Edition d’une offre collective',
    },
  },
  {
    lazy: () =>
      import(
        '@/pages/CollectiveOffer/CollectiveOfferStock/CollectiveOfferStockCreation/CollectiveOfferStockCreation'
      ),
    loader: withUserPermissions(mustBeOnboardedWithSelectedPartnerVenue),
    path: '/offre/:offerId/collectif/stocks',
    handle: {
      title: 'Dates et prix - Créer une offre réservable',
    },
  },
  {
    lazy: () =>
      import(
        '@/pages/CollectiveOffer/CollectiveOffer/CollectiveOfferCreation/CollectiveOfferCreation'
      ),
    loader: withUserPermissions(mustBeOnboardedWithSelectedPartnerVenue),
    path: '/offre/creation/collectif',
    handle: {
      title: 'Détails - Créer une offre réservable',
    },
  },
  {
    lazy: () =>
      import(
        '@/pages/CollectiveOffer/CollectiveOffer/CollectiveOfferCreation/CollectiveOfferCreation'
      ),
    loader: withUserPermissions(mustBeOnboardedWithSelectedPartnerVenue),
    path: '/offre/creation/collectif/vitrine',
    handle: {
      title: 'Détails - Créer une offre collective vitrine',
    },
  },
  {
    lazy: () =>
      import(
        '@/pages/CollectiveOffer/CollectiveOffer/CollectiveOfferCreation/CollectiveOfferCreation'
      ),
    loader: withUserPermissions(mustBeOnboardedWithSelectedPartnerVenue),
    path: '/offre/collectif/:offerId/creation',
    handle: {
      title: 'Détails - Créer une offre collective vitrine',
    },
  },
  {
    lazy: () =>
      import(
        '@/pages/CollectiveOffer/CollectiveOffer/CollectiveOfferCreation/CollectiveOfferCreation'
      ),
    loader: withUserPermissions(mustBeOnboardedWithSelectedPartnerVenue),
    path: '/offre/collectif/vitrine/:offerId/creation',
    handle: {
      title: 'Edition d’une offre collective',
    },
  },
  {
    lazy: () =>
      import(
        '@/pages/CollectiveOfferInstitution/CollectiveOfferCreationInstitution'
      ),
    loader: withUserPermissions(mustBeOnboardedWithSelectedPartnerVenue),
    path: '/offre/:offerId/collectif/etablissement',
    handle: {
      title: 'Établissement - Créer une offre réservable',
    },
  },
  {
    lazy: () =>
      import(
        '@/pages/CollectiveOffer/CollectiveOfferSummary/CollectiveOfferSummaryCreation/CollectiveOfferSummaryCreation'
      ),
    loader: withUserPermissions(mustBeOnboardedWithSelectedPartnerVenue),
    path: '/offre/:offerId/collectif/creation/recapitulatif',
    handle: {
      title: 'Récapitulatif - Créer une offre réservable',
    },
  },
  {
    lazy: () =>
      import(
        '@/pages/CollectiveOffer/CollectiveOfferPreview/CollectiveOfferPreviewCreation/CollectiveOfferPreviewCreation'
      ),
    loader: withUserPermissions(mustBeOnboardedWithSelectedPartnerVenue),
    path: '/offre/:offerId/collectif/creation/apercu',
    handle: {
      title: 'Aperçu - Créer une offre réservable',
    },
  },
  {
    lazy: () =>
      import(
        '@/pages/CollectiveOffer/CollectiveOfferPreview/CollectiveOfferPreviewCreation/CollectiveOfferPreviewCreation'
      ),
    loader: withUserPermissions(mustBeOnboardedWithSelectedPartnerVenue),
    path: '/offre/:offerId/collectif/vitrine/creation/apercu',
    handle: {
      title: 'Aperçu - Créer une offre vitrine',
    },
  },
  {
    lazy: () =>
      import(
        '@/pages/CollectiveOffer/CollectiveOfferSummary/CollectiveOfferSummaryCreation/CollectiveOfferSummaryCreation'
      ),
    loader: withUserPermissions(mustBeOnboardedWithSelectedPartnerVenue),
    path: '/offre/:offerId/collectif/vitrine/creation/recapitulatif',
    handle: {
      title: 'Récapitulatif - Créer une offre vitrine',
    },
  },
  {
    lazy: () =>
      import(
        '@/pages/CollectiveOffer/CollectiveOfferConfirmation/CollectiveOfferConfirmation'
      ),
    loader: withUserPermissions(mustBeOnboardedWithSelectedPartnerVenue),
    path: '/offre/:offerId/collectif/confirmation',
    handle: {
      title: 'Confirmation - Offre réservable publiée',
    },
  },
  {
    lazy: () =>
      import(
        '@/pages/CollectiveOffer/CollectiveOfferConfirmation/CollectiveOfferConfirmation'
      ),
    loader: withUserPermissions(mustBeOnboardedWithSelectedPartnerVenue),
    path: '/offre/:offerId/collectif/vitrine/confirmation',
    handle: {
      title: 'Confirmation - Offre collective vitrine publiée',
    },
  },
  {
    lazy: () =>
      import(
        '@/pages/CollectiveOffer/CollectiveOffer/CollectiveOfferEdition/CollectiveOfferEdition'
      ),
    loader: withUserPermissions(mustBeOnboardedWithSelectedPartnerVenue),
    path: '/offre/:offerId/collectif/edition',
    handle: {
      title: 'Détails - Modifier une offre collective réservable',
    },
  },
  {
    // @ts-expect-error `withCollectiveOfferFromParams` HOC seems to confuse the type checker.
    lazy: () =>
      import(
        '@/pages/CollectiveOffer/CollectiveOfferSummary/CollectiveOfferSummaryEdition/CollectiveOfferSummaryEdition'
      ),
    loader: withUserPermissions(mustBeOnboardedWithSelectedPartnerVenue),
    path: '/offre/:offerId/collectif/recapitulatif',
    handle: {
      title: 'Récapitulatif - Modifier une offre collective réservable',
    },
  },
  {
    lazy: () =>
      import(
        '@/pages/CollectiveOffer/CollectiveOfferPreview/CollectiveOfferPreviewEdition/CollectiveOfferPreviewEdition'
      ),
    loader: withUserPermissions(mustBeOnboardedWithSelectedPartnerVenue),
    path: '/offre/:offerId/collectif/vitrine/apercu',
    handle: {
      title: 'Aperçu - Prévisualisation d’une offre collective vitrine',
    },
  },
  {
    lazy: () =>
      import(
        '@/pages/CollectiveOffer/CollectiveOfferPreview/CollectiveOfferPreviewEdition/CollectiveOfferPreviewEdition'
      ),
    loader: withUserPermissions(mustBeOnboardedWithSelectedPartnerVenue),
    path: '/offre/:offerId/collectif/apercu',
    handle: {
      title: 'Aperçu - Prévisualisation d’une offre collective réservable',
    },
  },
  {
    lazy: () =>
      import(
        '@/pages/CollectiveOffer/CollectiveOfferStock/CollectiveOfferStockEdition/CollectiveOfferStockEdition'
      ),
    loader: withUserPermissions(mustBeOnboardedWithSelectedPartnerVenue),
    path: '/offre/:offerId/collectif/stocks/edition',
    handle: {
      title: 'Dates et prix - Modifier une offre collective réservable',
    },
  },
  {
    lazy: () =>
      import(
        '@/pages/CollectiveOfferInstitution/CollectiveOfferEditionInstitution'
      ),
    loader: withUserPermissions(mustBeOnboardedWithSelectedPartnerVenue),
    path: '/offre/:offerId/collectif/etablissement/edition',
    handle: {
      title: 'Établissement - Modifier une offre collective réservable',
    },
  },
  {
    lazy: () =>
      import('@/pages/CollectiveOfferFromRequest/CollectiveOfferFromRequest'),
    loader: withUserPermissions(mustBeOnboardedWithSelectedPartnerVenue),
    path: '/offre/collectif/creation/:offerId/requete/:requestId',
    handle: {
      title: 'Détails - Créer une offre réservable',
    },
  },
  {
    lazy: () => import('@/pages/ResetPassword/ResetPassword'),
    loader: withUserPermissions(mustBeUnauthenticated),
    path: '/demande-mot-de-passe/:token',
    handle: {
      title: 'Réinitialisez votre mot de passe',
    },
  },
  {
    element: <NavigateToNewPasswordReset to="/demande-mot-de-passe" />,
    loader: withUserPermissions(mustBeUnauthenticated),
    path: '/mot-de-passe-perdu',
    handle: {
      title: 'Réinitialisez votre mot de passe',
    },
  },
  {
    lazy: () => import('@/pages/LostPassword/LostPassword'),
    loader: withUserPermissions(mustBeUnauthenticated),
    path: '/demande-mot-de-passe',
    handle: {
      title: 'Réinitialisez votre mot de passe',
    },
  },
  {
    lazy: () => import('@/pages/IndividualOfferWizard/IndividualOfferWizard'),
    loader: withUserPermissions(mustBeOnboardedWithSelectedPartnerVenue),
    path: '/offre/individuelle',
    handle: {
      title: 'Offre étape par étape',
    },
    children: routesIndividualOfferWizard,
  },
  {
    lazy: () => import('@/pages/IndividualOfferWizard/IndividualOfferWizard'),
    loader: withUserPermissions(mustNotBeOnboardedWithSelectedPartnerVenue),
    path: '/onboarding/offre/individuelle',
    handle: {
      title: 'Offre étape par étape',
    },
    children: routesOnboardingIndividualOfferWizard,
  },
  {
    lazy: () => import('@/pages/User/UserProfile'),
    loader: withUserPermissions(mustBeAuthenticated),
    path: '/profil',
    handle: {
      title: 'Profil',
    },
  },
  {
    lazy: () => import('@/pages/SignupJourneyRoutes/SignupJourneyRoutes'),
    loader: withUserPermissions(mustBeAuthenticated),
    path: '/inscription/structure',
    handle: {
      title: "Parcours d'inscription",
    },
    children: routesSignupJourney,
  },
  {
    lazy: () => import('@/pages/Sitemap/Sitemap'),
    loader: withUserPermissions(mustBeAuthenticated),
    path: '/plan-du-site',
    handle: {
      title: 'Plan du site',
    },
  },
  {
    lazy: () => import('@/pages/Accessibility/AccessibilityMenu'),
    loader: noop,
    path: '/accessibilite',
    handle: {
      title: 'Informations d’accessibilité',
    },
  },
  {
    lazy: () => import('@/pages/Accessibility/Commitment'),
    loader: noop,
    path: '/accessibilite/engagements',
    handle: {
      title: 'Les engagements du pass Culture',
    },
  },
  {
    lazy: () => import('@/pages/Accessibility/Declaration'),
    loader: noop,
    path: '/accessibilite/declaration',
    handle: {
      title: "Déclaration d'accessibilité",
    },
  },
  {
    lazy: () => import('@/pages/Accessibility/MultiyearScheme'),
    loader: noop,
    path: '/accessibilite/schema-pluriannuel',
    handle: {
      title: 'Schéma pluriannuel',
    },
  },
  {
    loader: noop,
    path: '/ecoconception',
    handle: {
      title: 'Déclaration d’écoconception de l’espace partenaire',
    },
    children: routesEcoDesign,
  },
  {
    lazy: () =>
      import(
        '@/pages/Onboarding/OnboardingOffersTypeChoice/OnboardingOffersTypeChoice'
      ),
    loader: withUserPermissions(mustNotBeOnboardedWithSelectedPartnerVenue),
    path: '/onboarding',
    handle: {
      title: 'Onboarding',
    },
  },
  {
    lazy: () =>
      import(
        '@/pages/Onboarding/OnboardingOfferIndividual/OnboardingOfferIndividual'
      ),
    loader: withUserPermissions(
      (userPermissions) =>
        userPermissions.isAuthenticated &&
        !userPermissions.isSelectedPartnerVenueOnboarded
    ),
    path: '/onboarding/individuel',
    handle: {
      title: 'Offre à destination des jeunes - Onboarding',
    },
  },
  {
    lazy: () => import('@/pages/WelcomeCarousel/WelcomeCarousel'),
    loader: withUserPermissions(mustBeUnauthenticated),
    path: '/bienvenue',
    handle: {
      title: 'Bienvenue sur pass Culture Pro',
    },
    children: routesWelcomeCarousel,
  },
  {
    lazy: () => import('@/pages/Simulator/Simulator'),
    loader: withUserPermissions(mustBeUnauthenticated),
    path: '/inscription/preparation',
    handle: {
      title: 'Renseignez votre SIRET',
    },
    featureName: 'WIP_PRE_SIGNUP_SIMULATION',
    children: routesSimulator,
  },
  {
    lazy: () => import('@/pages/Errors/NotFound/NotFound'),
    loader: noop,
    path: '/404',
    handle: {
      title: 'Erreur 404 - Page indisponible',
      isErrorPage: true,
    },
  },
  {
    lazy: () => import('@/pages/NonAttached/NonAttached'),
    loader: withUserPermissions(
      (userPermissions) => !userPermissions.isSelectedPartnerVenueAssociated
    ),
    path: '/rattachement-en-cours',
    handle: {
      title: 'Rattachement en cours de traitement',
    },
  },
]
