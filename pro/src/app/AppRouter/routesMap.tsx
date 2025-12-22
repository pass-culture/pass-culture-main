/* No need to test this file */
/* istanbul ignore file */

import { Navigate, type NavigateProps, useLocation } from 'react-router'

import { parse } from '@/commons/utils/query-string'

import { RouteId } from './constants'
import {
  routesIndividualOfferWizard,
  routesOnboardingIndividualOfferWizard,
} from './subroutesIndividualOfferWizardMap'
import { routesReimbursements } from './subroutesReimbursements'
import { routesSignupJourney } from './subroutesSignupJourneyMap'
import { routesSignup } from './subroutesSignupMap'
import type { CustomRouteObject } from './types'
import {
  isPermissionless,
  mustBeAuthenticated,
  mustBeUnauthenticated,
  mustHaveAnAssociatedSelectedVenue,
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
    path: '/',
    title: 'Espace acteurs culturels',
    requiredPermissions: mustBeAuthenticated,
  },
  {
    id: RouteId.Hub,
    lazy: () => import('@/pages/Hub/Hub'),
    path: '/hub',
    title: 'Changer de structure',
    requiredPermissions: mustBeAuthenticated,
  },
  {
    path: '/adage-iframe/*',
    meta: { public: true },
    title: 'ADAGE',
    requiredPermissions: mustBeUnauthenticated,
    children: [
      {
        path: '*',
        meta: { public: true },
        title: 'ADAGE',
        lazy: () => import('@/pages/AdageIframe/app/App'),
        requiredPermissions: mustBeUnauthenticated,
      },
    ],
  },
  {
    lazy: () =>
      import(
        '@/pages/AdageIframe/app/components/UnauthenticatedError/UnauthenticatedError'
      ),
    path: '/adage-iframe/erreur',
    meta: { public: true },
    title: 'ADAGE',
    requiredPermissions: mustBeUnauthenticated,
  },
  {
    lazy: () => import('@/pages/Signup/Signup'),
    path: '/inscription',
    title: 'Créez votre compte',
    meta: { public: true },
    children: routesSignup,
    requiredPermissions: mustBeUnauthenticated,
  },
  {
    lazy: () => import('@/pages/Errors/Unavailable/Unavailable'),
    path: '/erreur/indisponible',
    title: 'Page indisponible',
    meta: { public: true, canBeLoggedIn: true },
    isErrorPage: true,
    requiredPermissions: isPermissionless,
  },
  {
    id: RouteId.Homepage,
    lazy: () => import('@/pages/Homepage/Homepage'),
    path: '/accueil',
    title: 'Espace acteurs culturels',
    requiredPermissions: mustHaveAnAssociatedSelectedVenue,
  },
  {
    lazy: () => import('@/pages/Desk/Desk'),
    path: '/guichet',
    title: 'Guichet',
    requiredPermissions: mustHaveAnAssociatedSelectedVenue,
  },
  {
    lazy: () => import('@/pages/Bookings/IndividualBookings'),
    path: '/reservations',
    title: 'Réservations individuelles',
    requiredPermissions: mustHaveAnAssociatedSelectedVenue,
  },
  {
    id: RouteId.Login,
    lazy: () => import('@/pages/SignIn/SignIn'),
    path: '/connexion',
    title: 'Connectez-vous',
    meta: { public: true },
    requiredPermissions: mustBeUnauthenticated,
  },
  {
    lazy: () => import('@/pages/EmailChangeValidation/EmailChangeValidation'),
    path: '/email_validation',
    title: 'Valider l’adresse email',
    meta: { public: true },
    requiredPermissions: mustBeUnauthenticated,
  },
  {
    element: <Navigate to="/collaborateurs" />,
    path: '/structures/:offererId',
    title: 'Détails de la structure',
    requiredPermissions: mustHaveAnAssociatedSelectedVenue,
  },
  {
    element: <Navigate to="/inscription/structure/recherche" />,
    path: '/structures/:offererId/lieux/creation',
    title: 'Créer un lieu',
    requiredPermissions: mustBeAuthenticated,
  },
  {
    lazy: () => import('@/pages/VenueEdition/VenueEdition'),
    path: '/structures/:offererId/lieux/:venueId/page-partenaire',
    title: 'Gérer ma page sur l’application',
    requiredPermissions: mustHaveAnAssociatedSelectedVenue,
    children: [
      {
        lazy: () => import('@/pages/VenueEdition/VenueEdition'),
        path: '*',
        title: 'Gérer ma page sur l’application',
        requiredPermissions: mustHaveAnAssociatedSelectedVenue,
      },
    ],
  },
  {
    lazy: () => import('@/pages/VenueEdition/VenueEdition'),
    path: '/structures/:offererId/lieux/:venueId/collectif',
    title: 'Gérer ma page sur ADAGE',
    requiredPermissions: mustHaveAnAssociatedSelectedVenue,
    children: [
      {
        lazy: () => import('@/pages/VenueEdition/VenueEdition'),
        path: '*',
        title: 'Gérer ma page sur ADAGE',
        requiredPermissions: mustHaveAnAssociatedSelectedVenue,
      },
    ],
  },
  {
    lazy: () => import('@/pages/VenueEdition/VenueEdition'),
    path: '/structures/:offererId/lieux/:venueId',
    title: 'Gérer ma page adresse',
    requiredPermissions: mustHaveAnAssociatedSelectedVenue,
    children: [
      {
        lazy: () => import('@/pages/VenueEdition/VenueEdition'),
        path: '*',
        title: 'Gérer ma page adresse',
        requiredPermissions: mustHaveAnAssociatedSelectedVenue,
      },
    ],
  },
  {
    lazy: () => import('@/pages/VenueSettings/VenueSettings'),
    path: '/structures/:offererId/lieux/:venueId/page-partenaire/parametres',
    title: 'Paramètres généraux',
    requiredPermissions: mustHaveAnAssociatedSelectedVenue,
  },
  {
    lazy: () => import('@/pages/VenueSettings/VenueSettings'),
    path: '/structures/:offererId/lieux/:venueId/collectif/parametres',
    title: 'Paramètres généraux',
    requiredPermissions: mustHaveAnAssociatedSelectedVenue,
  },
  {
    lazy: () => import('@/pages/VenueSettings/VenueSettings'),
    path: '/structures/:offererId/lieux/:venueId/parametres',
    title: 'Paramètres généraux',
    meta: {
      canBeOnboarding: true,
    },
    requiredPermissions: mustHaveAnAssociatedSelectedVenue,
  },
  {
    lazy: () => import('@/pages/CollectiveOffer/CollectiveOfferType/OfferType'),
    path: '/offre/creation',
    title: 'Créer une offre collective',
    requiredPermissions: mustHaveAnAssociatedSelectedVenue,
  },
  {
    lazy: () => import('@/pages/IndividualOffers/IndividualOffers'),
    path: '/offres',
    title: 'Offres individuelles',
    requiredPermissions: mustHaveAnAssociatedSelectedVenue,
  },
  {
    lazy: () => import('@/pages/CollectiveOffers/CollectiveOffers'),
    path: '/offres/collectives',
    title: 'Offres collectives',
    requiredPermissions: mustHaveAnAssociatedSelectedVenue,
  },
  {
    lazy: () =>
      import('@/pages/TemplateCollectiveOffers/TemplateCollectiveOffers'),
    path: '/offres/vitrines',
    title: 'Offres vitrines',
    requiredPermissions: mustHaveAnAssociatedSelectedVenue,
  },
  {
    lazy: () =>
      import(
        '@/pages/CollectiveOfferSelectionDuplication/CollectiveOfferSelectionDuplication'
      ),
    path: '/offre/creation/collectif/selection',
    title: 'Edition d’une offre collective',
    requiredPermissions: mustHaveAnAssociatedSelectedVenue,
  },
  {
    lazy: () =>
      import(
        '@/pages/CollectiveOffer/CollectiveOfferStock/CollectiveOfferStockCreation/CollectiveOfferStockCreation'
      ),
    path: '/offre/:offerId/collectif/stocks',
    title: 'Dates et prix - Créer une offre réservable',
    requiredPermissions: mustHaveAnAssociatedSelectedVenue,
  },
  {
    lazy: () =>
      import(
        '@/pages/CollectiveOffer/CollectiveOffer/CollectiveOfferCreation/CollectiveOfferCreation'
      ),
    path: '/offre/creation/collectif',
    title: 'Détails - Créer une offre réservable',
    requiredPermissions: mustHaveAnAssociatedSelectedVenue,
  },
  {
    lazy: () =>
      import(
        '@/pages/CollectiveOffer/CollectiveOffer/CollectiveOfferCreation/CollectiveOfferCreation'
      ),
    path: '/offre/creation/collectif/vitrine',
    title: 'Détails - Créer une offre collective vitrine',
    requiredPermissions: mustHaveAnAssociatedSelectedVenue,
  },
  {
    lazy: () =>
      import(
        '@/pages/CollectiveOffer/CollectiveOffer/CollectiveOfferCreation/CollectiveOfferCreation'
      ),
    path: '/offre/collectif/:offerId/creation',
    title: 'Détails - Créer une offre collective vitrine',
    requiredPermissions: mustHaveAnAssociatedSelectedVenue,
  },
  {
    lazy: () =>
      import(
        '@/pages/CollectiveOffer/CollectiveOffer/CollectiveOfferCreation/CollectiveOfferCreation'
      ),
    path: '/offre/collectif/vitrine/:offerId/creation',
    title: 'Edition d’une offre collective',
    requiredPermissions: mustHaveAnAssociatedSelectedVenue,
  },
  {
    lazy: () =>
      import(
        '@/pages/CollectiveOfferVisibility/CollectiveOfferCreationVisibility'
      ),
    path: '/offre/:offerId/collectif/visibilite',
    title: 'Visibilité - Créer une offre réservable',
    requiredPermissions: mustHaveAnAssociatedSelectedVenue,
  },
  {
    lazy: () =>
      import(
        '@/pages/CollectiveOffer/CollectiveOfferSummary/CollectiveOfferSummaryCreation/CollectiveOfferSummaryCreation'
      ),
    path: '/offre/:offerId/collectif/creation/recapitulatif',
    title: 'Récapitulatif - Créer une offre réservable',
    requiredPermissions: mustHaveAnAssociatedSelectedVenue,
  },
  {
    lazy: () =>
      import(
        '@/pages/CollectiveOffer/CollectiveOfferPreview/CollectiveOfferPreviewCreation/CollectiveOfferPreviewCreation'
      ),
    path: '/offre/:offerId/collectif/creation/apercu',
    title: 'Aperçu - Créer une offre réservable',
    requiredPermissions: mustHaveAnAssociatedSelectedVenue,
  },
  {
    lazy: () =>
      import(
        '@/pages/CollectiveOffer/CollectiveOfferPreview/CollectiveOfferPreviewCreation/CollectiveOfferPreviewCreation'
      ),
    path: '/offre/:offerId/collectif/vitrine/creation/apercu',
    title: 'Aperçu - Créer une offre vitrine',
    requiredPermissions: mustHaveAnAssociatedSelectedVenue,
  },
  {
    lazy: () =>
      import(
        '@/pages/CollectiveOffer/CollectiveOfferSummary/CollectiveOfferSummaryCreation/CollectiveOfferSummaryCreation'
      ),
    path: '/offre/:offerId/collectif/vitrine/creation/recapitulatif',
    title: 'Récapitulatif - Créer une offre vitrine',
    requiredPermissions: mustHaveAnAssociatedSelectedVenue,
  },
  {
    lazy: () =>
      import(
        '@/pages/CollectiveOffer/CollectiveOfferConfirmation/CollectiveOfferConfirmation'
      ),
    path: '/offre/:offerId/collectif/confirmation',
    title: 'Confirmation - Offre réservable publiée',
    requiredPermissions: mustHaveAnAssociatedSelectedVenue,
  },
  {
    lazy: () =>
      import(
        '@/pages/CollectiveOffer/CollectiveOfferConfirmation/CollectiveOfferConfirmation'
      ),
    path: '/offre/:offerId/collectif/vitrine/confirmation',
    title: 'Confirmation - Offre collective vitrine publiée',
    requiredPermissions: mustHaveAnAssociatedSelectedVenue,
  },
  {
    lazy: () =>
      import(
        '@/pages/CollectiveOffer/CollectiveOffer/CollectiveOfferEdition/CollectiveOfferEdition'
      ),
    path: '/offre/:offerId/collectif/edition',
    title: 'Détails - Modifier une offre collective réservable',
    requiredPermissions: mustHaveAnAssociatedSelectedVenue,
  },
  {
    // @ts-expect-error `withCollectiveOfferFromParams` HOC seems to confuse the type checker.
    lazy: () =>
      import(
        '@/pages/CollectiveOffer/CollectiveOfferSummary/CollectiveOfferSummaryEdition/CollectiveOfferSummaryEdition'
      ),
    path: '/offre/:offerId/collectif/recapitulatif',
    title: 'Récapitulatif - Modifier une offre collective réservable',
    requiredPermissions: mustHaveAnAssociatedSelectedVenue,
  },
  {
    lazy: () =>
      import(
        '@/pages/CollectiveOffer/CollectiveOfferPreview/CollectiveOfferPreviewEdition/CollectiveOfferPreviewEdition'
      ),
    path: '/offre/:offerId/collectif/vitrine/apercu',
    title: 'Aperçu - Prévisualisation d’une offre collective vitrine',
    requiredPermissions: mustHaveAnAssociatedSelectedVenue,
  },
  {
    lazy: () =>
      import(
        '@/pages/CollectiveOffer/CollectiveOfferPreview/CollectiveOfferPreviewEdition/CollectiveOfferPreviewEdition'
      ),
    path: '/offre/:offerId/collectif/apercu',
    title: 'Aperçu - Prévisualisation d’une offre collective réservable',
    requiredPermissions: mustHaveAnAssociatedSelectedVenue,
  },
  {
    lazy: () =>
      import(
        '@/pages/CollectiveOffer/CollectiveOfferStock/CollectiveOfferStockEdition/CollectiveOfferStockEdition'
      ),
    path: '/offre/:offerId/collectif/stocks/edition',
    title: 'Dates et prix - Modifier une offre collective réservable',
    requiredPermissions: mustHaveAnAssociatedSelectedVenue,
  },
  {
    lazy: () =>
      import(
        '@/pages/CollectiveOfferVisibility/CollectiveOfferEditionVisibility'
      ),
    path: '/offre/:offerId/collectif/visibilite/edition',
    title: 'Visibilité - Modifier une offre collective réservable',
    requiredPermissions: mustHaveAnAssociatedSelectedVenue,
  },
  {
    lazy: () =>
      import('@/pages/CollectiveOfferFromRequest/CollectiveOfferFromRequest'),
    path: '/offre/collectif/creation/:offerId/requete/:requestId',
    title: 'Détails - Créer une offre réservable',
    requiredPermissions: mustHaveAnAssociatedSelectedVenue,
  },
  {
    lazy: () => import('@/pages/ResetPassword/ResetPassword'),
    path: '/demande-mot-de-passe/:token',
    title: 'Réinitialisez votre mot de passe',
    meta: { public: true },
    // TODO (igabriele, 2025-12-18): Should we also allow this route for authenticated users?
    requiredPermissions: mustBeUnauthenticated,
  },
  {
    element: <NavigateToNewPasswordReset to="/demande-mot-de-passe" />,
    path: '/mot-de-passe-perdu',
    title: 'Réinitialisez votre mot de passe',
    meta: { public: true },
    // TODO (igabriele, 2025-12-18): Should we also allow this route for authenticated users?
    requiredPermissions: mustBeUnauthenticated,
  },
  {
    lazy: () => import('@/pages/LostPassword/LostPassword'),
    path: '/demande-mot-de-passe',
    title: 'Réinitialisez votre mot de passe',
    meta: { public: true },
    // TODO (igabriele, 2025-12-18): Should we also allow this route for authenticated users?
    requiredPermissions: mustBeUnauthenticated,
  },
  {
    lazy: () => import('@/pages/IndividualOfferWizard/IndividualOfferWizard'),
    path: '/offre/individuelle',
    title: 'Offre étape par étape',
    children: routesIndividualOfferWizard,
    requiredPermissions: mustHaveAnAssociatedSelectedVenue,
  },
  {
    lazy: () => import('@/pages/IndividualOfferWizard/IndividualOfferWizard'),
    path: '/onboarding/offre/individuelle',
    title: 'Offre étape par étape',
    children: routesOnboardingIndividualOfferWizard,
    meta: {
      onboardingOnly: true,
    },
    requiredPermissions: mustNotBeOnboarded,
  },
  {
    lazy: () => import('@/pages/Reimbursements/Reimbursements'),
    path: '/remboursements',
    title: 'Gestion financière',
    children: routesReimbursements,
    requiredPermissions: mustHaveAnAssociatedSelectedVenue,
  },
  {
    lazy: () => import('@/pages/User/UserProfile'),
    path: '/profil',
    title: 'Profil',
    meta: {
      canBeOnboarding: true,
    },
    requiredPermissions: mustBeAuthenticated,
  },
  {
    lazy: () => import('@/pages/SignupJourneyRoutes/SignupJourneyRoutes'),
    path: '/inscription/structure',
    title: "Parcours d'inscription",
    children: routesSignupJourney,
    requiredPermissions: mustBeAuthenticated,
  },
  {
    lazy: () => import('@/pages/Sitemap/Sitemap'),
    path: '/plan-du-site',
    title: 'Plan du site',
    requiredPermissions: mustBeAuthenticated,
  },
  {
    lazy: () => import('@/pages/Accessibility/AccessibilityMenu'),
    path: '/accessibilite',
    title: 'Informations d’accessibilité',
    meta: { public: true, canBeLoggedIn: true },
    requiredPermissions: isPermissionless,
  },
  {
    lazy: () => import('@/pages/Accessibility/Commitment'),
    path: '/accessibilite/engagements',
    title: 'Les engagements du pass Culture',
    meta: { public: true, canBeLoggedIn: true },
    requiredPermissions: isPermissionless,
  },
  {
    lazy: () => import('@/pages/Accessibility/Declaration'),
    path: '/accessibilite/declaration',
    title: "Déclaration d'accessibilité",
    meta: { public: true, canBeLoggedIn: true },
    requiredPermissions: isPermissionless,
  },
  {
    lazy: () => import('@/pages/Accessibility/MultiyearScheme'),
    path: '/accessibilite/schema-pluriannuel',
    title: 'Schéma pluriannuel',
    meta: { public: true, canBeLoggedIn: true },
    requiredPermissions: isPermissionless,
  },
  {
    lazy: () => import('@/pages/Collaborators/Collaborators'),
    path: '/collaborateurs',
    title: 'Collaborateurs',
    meta: {
      canBeOnboarding: true,
    },
    requiredPermissions: mustBeAuthenticated,
  },
  {
    lazy: () =>
      import(
        '@/pages/Onboarding/OnboardingOffersTypeChoice/OnboardingOffersTypeChoice'
      ),
    path: '/onboarding',
    title: 'Onboarding',
    meta: {
      onboardingOnly: true,
    },
    requiredPermissions: mustNotBeOnboarded,
  },
  {
    lazy: () =>
      import(
        '@/pages/Onboarding/OnboardingOfferIndividual/OnboardingOfferIndividual'
      ),
    path: '/onboarding/individuel',
    title: 'Offre à destination des jeunes - Onboarding',
    meta: {
      onboardingOnly: true,
    },
    requiredPermissions: (userPermissions) =>
      userPermissions.isAuthenticated && !userPermissions.isOnboarded,
  },
  {
    lazy: () => import('@/pages/Errors/NotFound/NotFound'),
    path: '/404',
    title: 'Erreur 404 - Page indisponible',
    isErrorPage: true,
    requiredPermissions: isPermissionless,
  },
  {
    id: RouteId.PendingVenuAssociation,
    lazy: () => import('@/pages/NonAttached/NonAttached'),
    path: '/rattachement-en-cours',
    title: 'Rattachement en cours de traitement',
    meta: {
      unattachedOnly: true,
    },
    requiredPermissions: (userPermissions) =>
      !userPermissions.isSelectedVenueAssociated,
  },
]
