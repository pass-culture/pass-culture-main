/* No need to test this file */
/* istanbul ignore file */
import React from 'react'
import { Navigate, useLocation } from 'react-router-dom'

import AdageIframe from 'pages/AdageIframe/AdageIframe'
import Bookings from 'pages/Bookings'
import CollectiveBookings from 'pages/CollectiveBookings'
import CollectiveOfferConfirmation from 'pages/CollectiveOfferConfirmation'
import CollectiveOfferCreation from 'pages/CollectiveOfferCreation'
import CollectiveOfferEdition from 'pages/CollectiveOfferEdition'
import CollectiveOffers from 'pages/CollectiveOffers'
import CollectiveOfferStockCreation from 'pages/CollectiveOfferStockCreation'
import CollectiveOfferStockEdition from 'pages/CollectiveOfferStockEdition'
import CollectiveOfferSummaryCreation from 'pages/CollectiveOfferSummaryCreation'
import CollectiveOfferSummaryEdition from 'pages/CollectiveOfferSummaryEdition'
import CollectiveOfferVisibilityCreation from 'pages/CollectiveOfferVisibility/CollectiveOfferCreationVisibility'
import CollectiveOfferVisibility from 'pages/CollectiveOfferVisibility/CollectiveOfferEditionVisibility'
import CsvTable from 'pages/CsvTable'
import Desk from 'pages/Desk'
import { EmailChangeValidation } from 'pages/EmailChangeValidation'
import Unavailable from 'pages/Errors/Unavailable/Unavailable'
import Homepage from 'pages/Home/Homepage'
import { Logout } from 'pages/Logout'
import LostPassword from 'pages/LostPassword'
import OffererDetails from 'pages/Offerers/Offerer/OffererDetails/OffererDetails'
import CollectiveDataEdition from 'pages/Offerers/Offerer/VenueV1/VenueEdition/CollectiveDataEdition'
import OffererCreation from 'pages/Offerers/OffererCreation'
import { OffererStats } from 'pages/OffererStats'
import { OfferIndividualWizard } from 'pages/OfferIndividualWizard'
import OffersRoute from 'pages/Offers'
import OfferType from 'pages/OfferType'
import Reimbursements from 'pages/Reimbursements'
import ResetPassword from 'pages/ResetPassword/ResetPassword'
import SignIn from 'pages/SignIn/SignIn'
import Signup from 'pages/Signup/Signup'
import { SignupJourneyRoutes } from 'pages/SignupJourneyRoutes'
import { UserProfile } from 'pages/User'
import { VenueCreation } from 'pages/VenueCreation'
import { VenueEdition } from 'pages/VenueEdition'
import CollectiveOfferSelectionDuplication from 'screens/CollectiveOfferSelectionDuplication'
import { UNAVAILABLE_ERROR_PAGE } from 'utils/routes'

export interface ILayoutConfig {
  pageName?: string
  fullscreen?: boolean
}

interface IRouteMeta {
  public?: boolean
  layoutConfig?: ILayoutConfig
  withoutLayout?: boolean
  shouldRedirect?: boolean
}
export interface IRoute {
  parentPath?: string
  path: string
  title?: string
  element: JSX.Element
  meta?: IRouteMeta
  featureName?: string
}

const RedirectToConnexionComponent = () => {
  const location = useLocation()
  return <Navigate to={`/connexion${location.search}`} />
}

const routes: IRoute[] = [
  {
    element: <RedirectToConnexionComponent />,
    path: '/',
    meta: { withoutLayout: true },
  },
  {
    element: <Logout />,
    path: '/logout',
    meta: { withoutLayout: true },
  },
  {
    element: <AdageIframe />,
    path: '/adage-iframe',
    meta: {
      public: true,
      withoutLayout: true,
    },
  },
  {
    element: <Signup />,
    path: '/inscription/*',
    title: 'Créer un compte',
    meta: {
      public: true,
      withoutLayout: true,
    },
  },
  {
    element: <CsvTable />,
    path: '/remboursements-details',
    title: 'Remboursements',
    meta: { withoutLayout: true },
  },
  {
    element: <Unavailable />,
    path: UNAVAILABLE_ERROR_PAGE,
    title: 'Erreur 404 - Page indisponible',
    meta: {
      public: true,
      withoutLayout: true,
    },
  },
  {
    element: <Homepage />,
    path: '/accueil',
    title: 'Espace acteurs culturels',
    meta: { shouldRedirect: true },
  },
  {
    element: <Desk />,
    path: '/guichet',
    title: 'Guichet',
  },
  {
    element: <Bookings />,
    path: '/reservations',
    title: 'Réservations individuelles',
    meta: { shouldRedirect: true },
  },
  {
    element: <CollectiveBookings />,
    path: '/reservations/collectives',
    title: 'Réservations collectives',
    meta: { shouldRedirect: true },
  },
  {
    element: <SignIn />,
    path: '/connexion',
    title: 'Se connecter',
    meta: {
      public: true,
      withoutLayout: true,
    },
  },
  {
    element: <EmailChangeValidation />,
    path: '/email_validation',
    title: 'Valider l’adresse e-mail',
    meta: {
      public: true,
      layoutConfig: {
        fullscreen: true,
        pageName: 'sign-in',
      },
    },
  },
  {
    element: <OffererCreation />,
    path: '/structures/creation',
    title: 'Créer une structure',
  },
  {
    element: <OffererDetails />,
    path: '/structures/:offererId',
    title: 'Détails de la structure',
    meta: { shouldRedirect: true },
  },
  {
    element: <VenueCreation />,
    path: '/structures/:offererId/lieux/creation',
    title: 'Créer un lieu',
    meta: { shouldRedirect: true },
  },
  {
    element: <VenueEdition />,
    path: '/structures/:offererId/lieux/:venueId',
    title: 'Modifier un lieu',
    meta: { shouldRedirect: true },
  },
  {
    element: <CollectiveDataEdition />,
    path: '/structures/:offererId/lieux/:venueId/eac',
    title: 'Modifier les informations pour les enseignants d’un lieu',
    meta: { shouldRedirect: true },
  },
  {
    element: <OfferType />,
    path: '/offre/creation',
    title: 'Selection du type d’offre',
    meta: { shouldRedirect: true },
  },
  {
    element: <OffersRoute />,
    path: '/offres',
    title: 'Offres individuelles',
    meta: { shouldRedirect: true },
  },
  {
    element: <CollectiveOffers />,
    path: '/offres/collectives',
    title: 'Offres collectives',
    meta: { shouldRedirect: true },
  },
  {
    element: <CollectiveOfferSelectionDuplication />,
    path: '/offre/creation/collectif/selection',
    title: 'Edition d’une offre collective',
  },
  {
    element: <CollectiveOfferStockCreation />,
    path: '/offre/:offerId/collectif/stocks',
    title: 'Date et prix - Créer une offre réservable',
    meta: { shouldRedirect: true },
  },
  {
    element: <CollectiveOfferCreation />,
    path: '/offre/creation/collectif',
    title: 'Détails - Créer une offre réservable',
    meta: { shouldRedirect: true },
  },
  {
    element: <CollectiveOfferCreation />,
    path: '/offre/creation/collectif/vitrine',
    title: 'Détails - Créer une offre collective vitrine',
    meta: { shouldRedirect: true },
  },
  {
    element: <CollectiveOfferCreation />,
    path: '/offre/collectif/:offerId/creation',
    title: 'Détails - Créer une offre collective vitrine',
    meta: { shouldRedirect: true },
  },
  {
    element: <CollectiveOfferCreation />,
    path: '/offre/collectif/vitrine/:offerId/creation',
    title: 'Edition d’une offre collective',
    meta: { shouldRedirect: true },
  },
  {
    element: <CollectiveOfferVisibilityCreation />,
    path: '/offre/:offerId/collectif/visibilite',
    title: 'Visibilité - Créer une offre réservable',
    meta: { shouldRedirect: true },
  },
  {
    element: <CollectiveOfferSummaryCreation />,
    path: '/offre/:offerId/collectif/creation/recapitulatif',
    title: 'Récapitulatif - Créer une offre réservable',
    meta: { shouldRedirect: true },
  },
  {
    element: <CollectiveOfferSummaryCreation />,
    path: '/offre/:offerId/collectif/vitrine/creation/recapitulatif',
    title: 'Récapitulatif - Modifier une offre réservable',
    meta: { shouldRedirect: true },
  },
  {
    element: <CollectiveOfferConfirmation />,
    path: '/offre/:offerId/collectif/confirmation',
    title: 'Confirmation - Offre réservable publiée',
    meta: { shouldRedirect: true },
  },
  {
    element: <CollectiveOfferConfirmation />,
    path: '/offre/:offerId/collectif/vitrine/confirmation',
    title: 'Confirmation - Offre collective vitrine publiée',
    meta: { shouldRedirect: true },
  },
  {
    element: <CollectiveOfferEdition />,
    path: '/offre/:offerId/collectif/edition',
    title: 'Détails - Modifier une offre réservable',
    meta: { shouldRedirect: true },
  },
  {
    element: <CollectiveOfferSummaryEdition />,
    path: '/offre/:offerId/collectif/recapitulatif',
    title: 'Edition d’une offre collective',
    meta: { shouldRedirect: true },
  },
  {
    element: <CollectiveOfferStockEdition />,
    path: '/offre/:offerId/collectif/stocks/edition',
    title: 'Date et prix - Modifier une offre réservable',
    meta: { shouldRedirect: true },
  },
  {
    element: <CollectiveOfferVisibility />,
    path: '/offre/:offerId/collectif/visibilite/edition',
    title: 'Visibilité - Modifier une offre réservable',
    meta: { shouldRedirect: true },
  },
  {
    element: <ResetPassword />,
    path: '/mot-de-passe-perdu',
    title: 'Définir un nouveau mot de passe',
    meta: {
      public: true,
      withoutLayout: true,
    },
  },
  {
    element: <LostPassword />,
    path: '/demande-mot-de-passe',
    title: 'Demander un nouveau mot de passe',
    meta: {
      public: true,
      withoutLayout: true,
    },
  },
  {
    element: <OfferIndividualWizard />,
    path: '/offre/individuelle/:offerId/*',
    title: 'Offre étape par étape',
    meta: { shouldRedirect: true },
  },
  {
    element: <Reimbursements />,
    path: '/remboursements/*',
    title: 'Remboursements',
    meta: {
      layoutConfig: {
        pageName: 'reimbursements',
      },
    },
  },
  {
    element: <UserProfile />,
    path: '/profil',
    title: 'Profil',
  },
  {
    element: <OffererStats />,
    path: '/statistiques',
    title: 'Statistiques',
    featureName: 'ENABLE_OFFERER_STATS',
  },
  {
    element: <SignupJourneyRoutes />,
    path: '/parcours-inscription/*',
    title: 'Parcours de souscription',
    featureName: 'WIP_ENABLE_NEW_ONBOARDING',
    meta: { withoutLayout: true },
  },
]

export default routes
