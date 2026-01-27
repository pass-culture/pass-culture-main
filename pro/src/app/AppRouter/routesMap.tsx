/* No need to test this file */
/* istanbul ignore file */

import { Navigate, type NavigateProps, useLocation } from 'react-router'

import { withUserPermissions } from '@/commons/auth/withUserPermissions'
import { noop } from '@/commons/utils/noop'
import { parse } from '@/commons/utils/query-string'

import {
  routesIndividualOfferWizard,
  routesOnboardingIndividualOfferWizard,
} from './subroutesIndividualOfferWizardMap'
import { routesReimbursements } from './subroutesReimbursements'
import { routesSignupJourney } from './subroutesSignupJourneyMap'
import { routesSignup } from './subroutesSignupMap'
import type { CustomRouteObject } from './types'
import {
  hasNewHomepage,
  mustBeAuthenticated,
  mustBeUnauthenticated,
  mustHaveSelectedVenue,
  mustNotBeOnboarded,
} from './utils'

const NavigateToNewPasswordReset = ({ to, ...props }: NavigateProps) => {
  const { search } = useLocation()
  const { token } = parse(search)
  return <Navigate {...props} to={`${to}/${token}`} />
}

export const routes: CustomRouteObject[] = [
  {
    element: <Navigate to="/accueil" />,
    loader: withUserPermissions(mustBeAuthenticated),
    path: '/',
    title: 'Espace acteurs culturels',
  },
  {
    lazy: () => import('@/pages/Hub/Hub'),
    loader: withUserPermissions(mustBeAuthenticated),
    path: '/hub',
    title: 'Changer de structure',
  },
  {
    path: '/adage-iframe/*',
    loader: withUserPermissions(mustBeUnauthenticated),
    meta: { public: true },
    title: 'ADAGE',
    children: [
      {
        path: '*',
        loader: withUserPermissions(mustBeUnauthenticated),
        meta: { public: true },
        title: 'ADAGE',
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
    meta: { public: true },
    title: 'ADAGE',
  },
  {
    lazy: () => import('@/pages/Signup/Signup'),
    loader: withUserPermissions(mustBeUnauthenticated),
    path: '/inscription',
    title: 'Créez votre compte',
    meta: { public: true },
    children: routesSignup,
  },
  {
    lazy: () => import('@/pages/Errors/Unavailable/Unavailable'),
    loader: noop,
    path: '/erreur/indisponible',
    title: 'Page indisponible',
    meta: { public: true, canBeLoggedIn: true },
    isErrorPage: true,
  },
  {
    lazy: () =>
      hasNewHomepage()
        ? import('@/pages/Homepage/NewHomepage')
        : import('@/pages/Homepage/Homepage'),
    loader: withUserPermissions(mustHaveSelectedVenue),
    path: '/accueil',
    title: 'Espace acteurs culturels',
  },
  {
    lazy: () => import('@/pages/Desk/Desk'),
    loader: withUserPermissions(mustHaveSelectedVenue),
    path: '/guichet',
    title: 'Guichet',
  },
  {
    lazy: () => import('@/pages/Bookings/IndividualBookings'),
    loader: withUserPermissions(mustHaveSelectedVenue),
    path: '/reservations',
    title: 'Réservations individuelles',
  },
  {
    lazy: () => import('@/pages/SignIn/SignIn'),
    loader: withUserPermissions(mustBeUnauthenticated),
    path: '/connexion',
    title: 'Connectez-vous',
    meta: { public: true },
  },
  {
    lazy: () => import('@/pages/EmailChangeValidation/EmailChangeValidation'),
    loader: withUserPermissions(mustBeUnauthenticated),
    path: '/email_validation',
    title: 'Valider l’adresse email',
    meta: { public: true },
  },
  {
    element: <Navigate to="/collaborateurs" />,
    loader: withUserPermissions(mustHaveSelectedVenue),
    path: '/structures/:offererId',
    title: 'Détails de la structure',
  },
  {
    element: <Navigate to="/inscription/structure/recherche" />,
    loader: withUserPermissions(mustBeAuthenticated),
    path: '/structures/:offererId/lieux/creation',
    title: 'Créer un lieu',
  },
  {
    lazy: () => import('@/pages/VenueEdition/VenueEdition'),
    loader: withUserPermissions(mustHaveSelectedVenue),
    path: '/structures/:offererId/lieux/:venueId/page-partenaire',
    title: 'Gérer ma page sur l’application',
    children: [
      {
        lazy: () => import('@/pages/VenueEdition/VenueEdition'),
        loader: withUserPermissions(mustHaveSelectedVenue),
        path: '*',
        title: 'Gérer ma page sur l’application',
      },
    ],
  },
  {
    lazy: () => import('@/pages/VenueEdition/VenueEdition'),
    loader: withUserPermissions(mustHaveSelectedVenue),
    path: '/structures/:offererId/lieux/:venueId/collectif',
    title: 'Gérer ma page sur ADAGE',
    children: [
      {
        lazy: () => import('@/pages/VenueEdition/VenueEdition'),
        loader: withUserPermissions(mustHaveSelectedVenue),
        path: '*',
        title: 'Gérer ma page sur ADAGE',
      },
    ],
  },
  {
    lazy: () => import('@/pages/VenueEdition/VenueEdition'),
    loader: withUserPermissions(mustHaveSelectedVenue),
    path: '/structures/:offererId/lieux/:venueId',
    title: 'Gérer ma page adresse',
    children: [
      {
        lazy: () => import('@/pages/VenueEdition/VenueEdition'),
        loader: withUserPermissions(mustHaveSelectedVenue),
        path: '*',
        title: 'Gérer ma page adresse',
      },
    ],
  },
  {
    lazy: () => import('@/pages/VenueSettings/VenueSettings'),
    loader: withUserPermissions(mustHaveSelectedVenue),
    path: '/structures/:offererId/lieux/:venueId/page-partenaire/parametres',
    title: 'Paramètres généraux',
  },
  {
    lazy: () => import('@/pages/VenueSettings/VenueSettings'),
    loader: withUserPermissions(mustHaveSelectedVenue),
    path: '/structures/:offererId/lieux/:venueId/collectif/parametres',
    title: 'Paramètres généraux',
  },
  {
    lazy: () => import('@/pages/VenueSettings/VenueSettings'),
    loader: withUserPermissions(mustHaveSelectedVenue),
    path: '/structures/:offererId/lieux/:venueId/parametres',
    title: 'Paramètres généraux',
    meta: {
      canBeOnboarding: true,
    },
  },
  {
    lazy: () => import('@/pages/CollectiveOffer/CollectiveOfferType/OfferType'),
    loader: withUserPermissions(mustHaveSelectedVenue),
    path: '/offre/creation',
    title: 'Créer une offre collective',
  },
  {
    lazy: () => import('@/pages/IndividualOffers/IndividualOffers'),
    loader: withUserPermissions(mustHaveSelectedVenue),
    path: '/offres',
    title: 'Offres individuelles',
  },
  {
    lazy: () => import('@/pages/CollectiveOffers/CollectiveOffers'),
    loader: withUserPermissions(mustHaveSelectedVenue),
    path: '/offres/collectives',
    title: 'Offres collectives',
  },
  {
    lazy: () =>
      import('@/pages/TemplateCollectiveOffers/TemplateCollectiveOffers'),
    loader: withUserPermissions(mustHaveSelectedVenue),
    path: '/offres/vitrines',
    title: 'Offres vitrines',
  },
  {
    lazy: () =>
      import(
        '@/pages/CollectiveOfferSelectionDuplication/CollectiveOfferSelectionDuplication'
      ),
    loader: withUserPermissions(mustHaveSelectedVenue),
    path: '/offre/creation/collectif/selection',
    title: 'Edition d’une offre collective',
  },
  {
    lazy: () =>
      import(
        '@/pages/CollectiveOffer/CollectiveOfferStock/CollectiveOfferStockCreation/CollectiveOfferStockCreation'
      ),
    loader: withUserPermissions(mustHaveSelectedVenue),
    path: '/offre/:offerId/collectif/stocks',
    title: 'Dates et prix - Créer une offre réservable',
  },
  {
    lazy: () =>
      import(
        '@/pages/CollectiveOffer/CollectiveOffer/CollectiveOfferCreation/CollectiveOfferCreation'
      ),
    loader: withUserPermissions(mustHaveSelectedVenue),
    path: '/offre/creation/collectif',
    title: 'Détails - Créer une offre réservable',
  },
  {
    lazy: () =>
      import(
        '@/pages/CollectiveOffer/CollectiveOffer/CollectiveOfferCreation/CollectiveOfferCreation'
      ),
    loader: withUserPermissions(mustHaveSelectedVenue),
    path: '/offre/creation/collectif/vitrine',
    title: 'Détails - Créer une offre collective vitrine',
  },
  {
    lazy: () =>
      import(
        '@/pages/CollectiveOffer/CollectiveOffer/CollectiveOfferCreation/CollectiveOfferCreation'
      ),
    loader: withUserPermissions(mustHaveSelectedVenue),
    path: '/offre/collectif/:offerId/creation',
    title: 'Détails - Créer une offre collective vitrine',
  },
  {
    lazy: () =>
      import(
        '@/pages/CollectiveOffer/CollectiveOffer/CollectiveOfferCreation/CollectiveOfferCreation'
      ),
    loader: withUserPermissions(mustHaveSelectedVenue),
    path: '/offre/collectif/vitrine/:offerId/creation',
    title: 'Edition d’une offre collective',
  },
  {
    lazy: () =>
      import(
        '@/pages/CollectiveOfferVisibility/CollectiveOfferCreationVisibility'
      ),
    loader: withUserPermissions(mustHaveSelectedVenue),
    path: '/offre/:offerId/collectif/visibilite',
    title: 'Visibilité - Créer une offre réservable',
  },
  {
    lazy: () =>
      import(
        '@/pages/CollectiveOffer/CollectiveOfferSummary/CollectiveOfferSummaryCreation/CollectiveOfferSummaryCreation'
      ),
    loader: withUserPermissions(mustHaveSelectedVenue),
    path: '/offre/:offerId/collectif/creation/recapitulatif',
    title: 'Récapitulatif - Créer une offre réservable',
  },
  {
    lazy: () =>
      import(
        '@/pages/CollectiveOffer/CollectiveOfferPreview/CollectiveOfferPreviewCreation/CollectiveOfferPreviewCreation'
      ),
    loader: withUserPermissions(mustHaveSelectedVenue),
    path: '/offre/:offerId/collectif/creation/apercu',
    title: 'Aperçu - Créer une offre réservable',
  },
  {
    lazy: () =>
      import(
        '@/pages/CollectiveOffer/CollectiveOfferPreview/CollectiveOfferPreviewCreation/CollectiveOfferPreviewCreation'
      ),
    loader: withUserPermissions(mustHaveSelectedVenue),
    path: '/offre/:offerId/collectif/vitrine/creation/apercu',
    title: 'Aperçu - Créer une offre vitrine',
  },
  {
    lazy: () =>
      import(
        '@/pages/CollectiveOffer/CollectiveOfferSummary/CollectiveOfferSummaryCreation/CollectiveOfferSummaryCreation'
      ),
    loader: withUserPermissions(mustHaveSelectedVenue),
    path: '/offre/:offerId/collectif/vitrine/creation/recapitulatif',
    title: 'Récapitulatif - Créer une offre vitrine',
  },
  {
    lazy: () =>
      import(
        '@/pages/CollectiveOffer/CollectiveOfferConfirmation/CollectiveOfferConfirmation'
      ),
    loader: withUserPermissions(mustHaveSelectedVenue),
    path: '/offre/:offerId/collectif/confirmation',
    title: 'Confirmation - Offre réservable publiée',
  },
  {
    lazy: () =>
      import(
        '@/pages/CollectiveOffer/CollectiveOfferConfirmation/CollectiveOfferConfirmation'
      ),
    loader: withUserPermissions(mustHaveSelectedVenue),
    path: '/offre/:offerId/collectif/vitrine/confirmation',
    title: 'Confirmation - Offre collective vitrine publiée',
  },
  {
    lazy: () =>
      import(
        '@/pages/CollectiveOffer/CollectiveOffer/CollectiveOfferEdition/CollectiveOfferEdition'
      ),
    loader: withUserPermissions(mustHaveSelectedVenue),
    path: '/offre/:offerId/collectif/edition',
    title: 'Détails - Modifier une offre collective réservable',
  },
  {
    // @ts-expect-error `withCollectiveOfferFromParams` HOC seems to confuse the type checker.
    lazy: () =>
      import(
        '@/pages/CollectiveOffer/CollectiveOfferSummary/CollectiveOfferSummaryEdition/CollectiveOfferSummaryEdition'
      ),
    loader: withUserPermissions(mustHaveSelectedVenue),
    path: '/offre/:offerId/collectif/recapitulatif',
    title: 'Récapitulatif - Modifier une offre collective réservable',
  },
  {
    lazy: () =>
      import(
        '@/pages/CollectiveOffer/CollectiveOfferPreview/CollectiveOfferPreviewEdition/CollectiveOfferPreviewEdition'
      ),
    loader: withUserPermissions(mustHaveSelectedVenue),
    path: '/offre/:offerId/collectif/vitrine/apercu',
    title: 'Aperçu - Prévisualisation d’une offre collective vitrine',
  },
  {
    lazy: () =>
      import(
        '@/pages/CollectiveOffer/CollectiveOfferPreview/CollectiveOfferPreviewEdition/CollectiveOfferPreviewEdition'
      ),
    loader: withUserPermissions(mustHaveSelectedVenue),
    path: '/offre/:offerId/collectif/apercu',
    title: 'Aperçu - Prévisualisation d’une offre collective réservable',
  },
  {
    lazy: () =>
      import(
        '@/pages/CollectiveOffer/CollectiveOfferStock/CollectiveOfferStockEdition/CollectiveOfferStockEdition'
      ),
    loader: withUserPermissions(mustHaveSelectedVenue),
    path: '/offre/:offerId/collectif/stocks/edition',
    title: 'Dates et prix - Modifier une offre collective réservable',
  },
  {
    lazy: () =>
      import(
        '@/pages/CollectiveOfferVisibility/CollectiveOfferEditionVisibility'
      ),
    loader: withUserPermissions(mustHaveSelectedVenue),
    path: '/offre/:offerId/collectif/visibilite/edition',
    title: 'Visibilité - Modifier une offre collective réservable',
  },
  {
    lazy: () =>
      import('@/pages/CollectiveOfferFromRequest/CollectiveOfferFromRequest'),
    loader: withUserPermissions(mustHaveSelectedVenue),
    path: '/offre/collectif/creation/:offerId/requete/:requestId',
    title: 'Détails - Créer une offre réservable',
  },
  {
    lazy: () => import('@/pages/ResetPassword/ResetPassword'),
    loader: withUserPermissions(mustBeUnauthenticated),
    path: '/demande-mot-de-passe/:token',
    title: 'Réinitialisez votre mot de passe',
    meta: { public: true },
  },
  {
    element: <NavigateToNewPasswordReset to="/demande-mot-de-passe" />,
    loader: withUserPermissions(mustBeUnauthenticated),
    path: '/mot-de-passe-perdu',
    title: 'Réinitialisez votre mot de passe',
    meta: { public: true },
  },
  {
    lazy: () => import('@/pages/LostPassword/LostPassword'),
    loader: withUserPermissions(mustBeUnauthenticated),
    path: '/demande-mot-de-passe',
    title: 'Réinitialisez votre mot de passe',
    meta: { public: true },
  },
  {
    lazy: () => import('@/pages/IndividualOfferWizard/IndividualOfferWizard'),
    loader: withUserPermissions(mustHaveSelectedVenue),
    path: '/offre/individuelle',
    title: 'Offre étape par étape',
    children: routesIndividualOfferWizard,
  },
  {
    lazy: () => import('@/pages/IndividualOfferWizard/IndividualOfferWizard'),
    loader: withUserPermissions(mustNotBeOnboarded),
    path: '/onboarding/offre/individuelle',
    title: 'Offre étape par étape',
    children: routesOnboardingIndividualOfferWizard,
    meta: {
      onboardingOnly: true,
    },
  },
  {
    lazy: () => import('@/pages/Reimbursements/Reimbursements'),
    loader: withUserPermissions(mustHaveSelectedVenue),
    path: '/remboursements',
    title: 'Gestion financière',
    children: routesReimbursements,
  },
  {
    lazy: () => import('@/pages/User/UserProfile'),
    loader: withUserPermissions(mustBeAuthenticated),
    path: '/profil',
    title: 'Profil',
    meta: {
      canBeOnboarding: true,
    },
  },
  {
    lazy: () => import('@/pages/SignupJourneyRoutes/SignupJourneyRoutes'),
    loader: withUserPermissions(mustBeAuthenticated),
    path: '/inscription/structure',
    title: "Parcours d'inscription",
    children: routesSignupJourney,
  },
  {
    lazy: () => import('@/pages/Sitemap/Sitemap'),
    loader: withUserPermissions(mustBeAuthenticated),
    path: '/plan-du-site',
    title: 'Plan du site',
  },
  {
    lazy: () => import('@/pages/Accessibility/AccessibilityMenu'),
    loader: noop,
    path: '/accessibilite',
    title: 'Informations d’accessibilité',
    meta: { public: true, canBeLoggedIn: true },
  },
  {
    lazy: () => import('@/pages/Accessibility/Commitment'),
    loader: noop,
    path: '/accessibilite/engagements',
    title: 'Les engagements du pass Culture',
    meta: { public: true, canBeLoggedIn: true },
  },
  {
    lazy: () => import('@/pages/Accessibility/Declaration'),
    loader: noop,
    path: '/accessibilite/declaration',
    title: "Déclaration d'accessibilité",
    meta: { public: true, canBeLoggedIn: true },
  },
  {
    lazy: () => import('@/pages/Accessibility/MultiyearScheme'),
    loader: noop,
    path: '/accessibilite/schema-pluriannuel',
    title: 'Schéma pluriannuel',
    meta: { public: true, canBeLoggedIn: true },
  },
  {
    lazy: () => import('@/pages/Collaborators/Collaborators'),
    loader: withUserPermissions(mustBeAuthenticated),
    path: '/collaborateurs',
    title: 'Collaborateurs',
    meta: {
      canBeOnboarding: true,
    },
  },
  {
    lazy: () =>
      import(
        '@/pages/Onboarding/OnboardingOffersTypeChoice/OnboardingOffersTypeChoice'
      ),
    loader: withUserPermissions(mustNotBeOnboarded),
    path: '/onboarding',
    title: 'Onboarding',
    meta: {
      onboardingOnly: true,
    },
  },
  {
    lazy: () =>
      import(
        '@/pages/Onboarding/OnboardingOfferIndividual/OnboardingOfferIndividual'
      ),
    loader: withUserPermissions(
      (userPermissions) =>
        userPermissions.isAuthenticated && !userPermissions.isOnboarded
    ),
    path: '/onboarding/individuel',
    title: 'Offre à destination des jeunes - Onboarding',
    meta: {
      onboardingOnly: true,
    },
  },
  {
    lazy: () => import('@/pages/Errors/NotFound/NotFound'),
    loader: noop,
    path: '/404',
    title: 'Erreur 404 - Page indisponible',
    isErrorPage: true,
  },
  {
    lazy: () => import('@/pages/NonAttached/NonAttached'),
    loader: withUserPermissions(
      (userPermissions) => !userPermissions.isSelectedVenueAssociated
    ),
    path: '/rattachement-en-cours',
    title: 'Rattachement en cours de traitement',
    meta: {
      unattachedOnly: true,
    },
  },
]
