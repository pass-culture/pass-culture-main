/* No need to test this file */
/* istanbul ignore file */

import React from 'react'
import { Navigate } from 'react-router-dom'

import { UNAVAILABLE_ERROR_PAGE } from 'utils/routes'

import { routesIndividualOfferWizard } from './subroutesIndividualOfferWizardMap'
import { routesReimbursements } from './subroutesReimbursements'
import { routesSignupJourney } from './subroutesSignupJourneyMap'
import { routesSignup } from './subroutesSignupMap'

interface RouteMeta {
  public?: boolean
}

export interface RouteConfig {
  path: string
  title: string
  element?: JSX.Element
  lazy?: any
  meta?: RouteMeta
  featureName?: string
  children?: RouteConfig[]
}

export const routes: RouteConfig[] = [
  {
    element: <Navigate to="/accueil" />,
    path: '/',
    title: 'Espace acteurs culturels',
  },
  {
    lazy: () => import('pages/AdageIframe/app/App'),
    path: '/adage-iframe/*',
    meta: { public: true },
    title: 'ADAGE',
  },
  {
    lazy: () =>
      import(
        'pages/AdageIframe/app/components/UnauthenticatedError/UnauthenticatedError'
      ),
    path: '/adage-iframe/erreur',
    meta: { public: true },
    title: 'ADAGE',
  },
  {
    lazy: () => import('pages/Signup/Signup'),
    path: '/inscription',
    title: 'Créer un compte',
    meta: { public: true },
    children: routesSignup,
  },
  {
    lazy: () => import('pages/Errors/Unavailable/Unavailable'),
    path: UNAVAILABLE_ERROR_PAGE,
    title: 'Page indisponible',
    meta: { public: true },
  },
  {
    lazy: () => import('pages/Home/Homepage'),
    path: '/accueil',
    title: 'Espace acteurs culturels',
  },
  {
    lazy: () => import('pages/Desk/Desk'),
    path: '/guichet',
    title: 'Guichet',
  },
  {
    lazy: () => import('pages/Bookings/Bookings'),
    path: '/reservations',
    title: 'Réservations individuelles',
  },
  {
    lazy: () => import('pages/CollectiveBookings/CollectiveBookings'),
    path: '/reservations/collectives',
    title: 'Réservations collectives',
  },
  {
    lazy: () => import('pages/SignIn/SignIn'),
    path: '/connexion',
    title: 'Se connecter',
    meta: { public: true },
  },
  {
    lazy: () => import('pages/EmailChangeValidation/EmailChangeValidation'),
    path: '/email_validation',
    title: 'Valider l’adresse email',
    meta: { public: true },
  },
  {
    element: <Navigate to="/collaborateurs" />,
    path: '/structures/:offererId',
    title: 'Détails de la structure',
  },
  {
    lazy: () => import('pages/VenueCreation/VenueCreation'),
    path: '/structures/:offererId/lieux/creation',
    title: 'Créer un lieu',
  },
  {
    lazy: () => import('pages/VenueEdition/VenueEdition'),
    path: '/structures/:offererId/lieux/:venueId/*',
    title: 'Gérer ma page sur l’application',
  },
  {
    lazy: () => import('pages/VenueSettings/VenueSettings'),
    path: '/structures/:offererId/lieux/:venueId/parametres',
    title: 'Paramètres généraux',
  },
  {
    lazy: () => import('pages/OfferType/OfferType'),
    path: '/offre/creation',
    title: 'Choix de la nature de l’offre - Créer une offre',
  },
  {
    lazy: () => import('pages/Offers/OffersRoute'),
    path: '/offres',
    title: 'Offres individuelles',
  },
  {
    lazy: () => import('pages/CollectiveOffers/CollectiveOffers'),
    path: '/offres/collectives',
    title: 'Offres collectives',
  },
  {
    lazy: () =>
      import(
        'screens/CollectiveOfferSelectionDuplication/CollectiveOfferSelectionDuplicationScreen'
      ),
    path: '/offre/creation/collectif/selection',
    title: 'Edition d’une offre collective',
  },
  {
    lazy: () =>
      import('pages/CollectiveOfferStockCreation/CollectiveOfferStockCreation'),
    path: '/offre/:offerId/collectif/stocks',
    title: 'Dates et prix - Créer une offre réservable',
  },
  {
    lazy: () => import('pages/CollectiveOfferCreation/CollectiveOfferCreation'),
    path: '/offre/creation/collectif',
    title: 'Détails - Créer une offre réservable',
  },
  {
    lazy: () => import('pages/CollectiveOfferCreation/CollectiveOfferCreation'),
    path: '/offre/creation/collectif/vitrine',
    title: 'Détails - Créer une offre collective vitrine',
  },
  {
    lazy: () => import('pages/CollectiveOfferCreation/CollectiveOfferCreation'),
    path: '/offre/collectif/:offerId/creation',
    title: 'Détails - Créer une offre collective vitrine',
  },
  {
    lazy: () => import('pages/CollectiveOfferCreation/CollectiveOfferCreation'),
    path: '/offre/collectif/vitrine/:offerId/creation',
    title: 'Edition d’une offre collective',
  },
  {
    lazy: () =>
      import(
        'pages/CollectiveOfferVisibility/CollectiveOfferCreationVisibility'
      ),
    path: '/offre/:offerId/collectif/visibilite',
    title: 'Visibilité - Créer une offre réservable',
  },
  {
    lazy: () =>
      import(
        'pages/CollectiveOfferSummaryCreation/CollectiveOfferSummaryCreation'
      ),
    path: '/offre/:offerId/collectif/creation/recapitulatif',
    title: 'Récapitulatif - Créer une offre réservable',
  },
  {
    lazy: () =>
      import(
        'pages/CollectiveOfferPreviewCreation/CollectiveOfferPreviewCreation'
      ),
    path: '/offre/:offerId/collectif/creation/apercu',
    title: 'Aperçu - Créer une offre réservable',
  },
  {
    lazy: () =>
      import(
        'pages/CollectiveOfferPreviewCreation/CollectiveOfferPreviewCreation'
      ),
    path: '/offre/:offerId/collectif/vitrine/creation/apercu',
    title: 'Aperçu - Créer une offre vitrine',
  },
  {
    lazy: () =>
      import(
        'pages/CollectiveOfferSummaryCreation/CollectiveOfferSummaryCreation'
      ),
    path: '/offre/:offerId/collectif/vitrine/creation/recapitulatif',
    title: 'Récapitulatif - Modifier une offre réservable',
  },
  {
    lazy: () =>
      import('pages/CollectiveOfferConfirmation/CollectiveOfferConfirmation'),
    path: '/offre/:offerId/collectif/confirmation',
    title: 'Confirmation - Offre réservable publiée',
  },
  {
    lazy: () =>
      import('pages/CollectiveOfferConfirmation/CollectiveOfferConfirmation'),
    path: '/offre/:offerId/collectif/vitrine/confirmation',
    title: 'Confirmation - Offre collective vitrine publiée',
  },
  {
    lazy: () => import('pages/CollectiveOfferEdition/CollectiveOfferEdition'),
    path: '/offre/:offerId/collectif/edition',
    title: 'Détails - Modifier une offre collective réservable',
  },
  {
    lazy: () =>
      import(
        'pages/CollectiveOfferSummaryEdition/CollectiveOfferSummaryEdition'
      ),
    path: '/offre/:offerId/collectif/recapitulatif',
    title: 'Récapitulatif - Modifier une offre collective réservable',
  },
  {
    lazy: () =>
      import(
        'pages/CollectiveOfferPreviewEdition/CollectiveOfferPreviewEdition'
      ),
    path: '/offre/:offerId/collectif/vitrine/apercu',
    title: 'Aperçu - Prévisualisation d’une offre collective vitrine',
  },
  {
    lazy: () =>
      import(
        'pages/CollectiveOfferPreviewEdition/CollectiveOfferPreviewEdition'
      ),
    path: '/offre/:offerId/collectif/apercu',
    title: 'Aperçu - Prévisualisation d’une offre collective réservable',
  },
  {
    lazy: () =>
      import('pages/CollectiveOfferStockEdition/CollectiveOfferStockEdition'),
    path: '/offre/:offerId/collectif/stocks/edition',
    title: 'Dates et prix - Modifier une offre collective réservable',
  },
  {
    lazy: () =>
      import(
        'pages/CollectiveOfferVisibility/CollectiveOfferEditionVisibility'
      ),
    path: '/offre/:offerId/collectif/visibilite/edition',
    title: 'Visibilité - Modifier une offre collective réservable',
  },
  {
    lazy: () =>
      import('pages/CollectiveOfferFromRequest/CollectiveOfferFromRequest'),
    path: '/offre/collectif/creation/:offerId/requete/:requestId',
    title: 'Détails - Créer une offre réservable',
  },
  {
    lazy: () => import('pages/ResetPassword/ResetPassword'),
    path: '/mot-de-passe-perdu',
    title: 'Définir un nouveau mot de passe',
    meta: { public: true },
  },
  {
    lazy: () => import('pages/LostPassword/LostPassword'),
    path: '/demande-mot-de-passe',
    title: 'Demander un nouveau mot de passe',
    meta: { public: true },
  },
  {
    lazy: () => import('pages/IndividualOfferWizard/IndividualOfferWizard'),
    path: '/offre/individuelle/:offerId',
    title: 'Offre étape par étape',
    children: routesIndividualOfferWizard,
  },
  {
    lazy: () => import('pages/Reimbursements/Reimbursements'),
    path: '/remboursements',
    title: 'Gestion financière',
    children: routesReimbursements,
  },
  {
    lazy: () => import('pages/User/UserProfile'),
    path: '/profil',
    title: 'Profil',
  },
  {
    lazy: () => import('pages/OffererStats/OffererStats'),
    path: '/statistiques',
    title: 'Statistiques',
    featureName: 'ENABLE_OFFERER_STATS',
  },
  {
    lazy: () => import('pages/SignupJourneyRoutes/SignupJourneyRoutes'),
    path: '/parcours-inscription',
    title: 'Parcours de souscription',
    children: routesSignupJourney,
  },
  {
    lazy: () => import('pages/Sitemap/Sitemap'),
    path: '/plan-du-site',
    title: 'Plan du site',
  },
  {
    lazy: () => import('pages/Accessibility/AccessibilityMenu'),
    path: '/accessibilite',
    title: 'Informations d’accessibilité',
    meta: { public: true },
  },
  {
    lazy: () => import('pages/Accessibility/Commitment'),
    path: '/accessibilite/engagements',
    title: 'Les engagements du pass Culture',
    meta: { public: true },
  },
  {
    lazy: () => import('pages/Accessibility/Declaration'),
    path: '/accessibilite/declaration',
    title: "Déclaration d'accessibilité",
    meta: { public: true },
  },
  {
    lazy: () => import('pages/Accessibility/MultiyearScheme'),
    path: '/accessibilite/schema-pluriannuel',
    title: 'Schéma pluriannuel',
    meta: { public: true },
  },
  {
    lazy: () => import('pages/Collaborators/Collaborators'),
    path: '/collaborateurs',
    title: 'Collaborateurs',
  },
  {
    lazy: () => import('pages/Errors/NotFound/NotFound'),
    path: '/404',
    title: 'Erreur 404 - Page indisponible',
  },
]
