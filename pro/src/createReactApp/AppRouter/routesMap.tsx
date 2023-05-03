/* No need to test this file */
/* istanbul ignore file */
import React from 'react'
import { Navigate, useLocation } from 'react-router-dom'

import AdageIframe from 'deprecatedPages/AdageIframe/AdageIframe'
import Bookings from 'deprecatedPages/Bookings'
import CollectiveBookings from 'deprecatedPages/CollectiveBookings'
import CollectiveOfferConfirmation from 'deprecatedPages/CollectiveOfferConfirmation'
import CollectiveOfferCreation from 'deprecatedPages/CollectiveOfferCreation'
import CollectiveOfferEdition from 'deprecatedPages/CollectiveOfferEdition'
import CollectiveOffers from 'deprecatedPages/CollectiveOffers'
import CollectiveOfferStockCreation from 'deprecatedPages/CollectiveOfferStockCreation'
import CollectiveOfferStockEdition from 'deprecatedPages/CollectiveOfferStockEdition'
import CollectiveOfferSummaryCreation from 'deprecatedPages/CollectiveOfferSummaryCreation'
import CollectiveOfferSummaryEdition from 'deprecatedPages/CollectiveOfferSummaryEdition'
import CollectiveOfferVisibilityCreation from 'deprecatedPages/CollectiveOfferVisibility/CollectiveOfferCreationVisibility'
import CollectiveOfferVisibility from 'deprecatedPages/CollectiveOfferVisibility/CollectiveOfferEditionVisibility'
import CsvTable from 'deprecatedPages/CsvTable'
import Desk from 'deprecatedPages/Desk'
import { EmailChangeValidation } from 'deprecatedPages/EmailChangeValidation'
import Unavailable from 'deprecatedPages/Errors/Unavailable/Unavailable'
import Homepage from 'deprecatedPages/Home/Homepage'
import { Logout } from 'deprecatedPages/Logout'
import LostPassword from 'deprecatedPages/LostPassword'
import OffererDetails from 'deprecatedPages/Offerers/Offerer/OffererDetails/OffererDetails'
import CollectiveDataEdition from 'deprecatedPages/Offerers/Offerer/VenueV1/VenueEdition/CollectiveDataEdition'
import OffererCreation from 'deprecatedPages/Offerers/OffererCreation'
import { OffererStats } from 'deprecatedPages/OffererStats'
import { OfferIndividualWizard } from 'deprecatedPages/OfferIndividualWizard'
import OffersRoute from 'deprecatedPages/Offers'
import OfferType from 'deprecatedPages/OfferType'
import Reimbursements from 'deprecatedPages/Reimbursements'
import ResetPassword from 'deprecatedPages/ResetPassword/ResetPassword'
import SignIn from 'deprecatedPages/SignIn/SignIn'
import Signup from 'deprecatedPages/Signup/Signup'
import { SignupJourneyRoutes } from 'deprecatedPages/SignupJourneyRoutes'
import { UserProfile } from 'deprecatedPages/User'
import { VenueCreation } from 'deprecatedPages/VenueCreation'
import { VenueEdition } from 'deprecatedPages/VenueEdition'
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
    path: '/inscription',
    title: 'Inscription',
    meta: {
      public: true,
      withoutLayout: true,
    },
  },
  {
    element: <Signup />,
    path: '/inscription/*',
    title: 'Inscription',
    meta: {
      public: true,
      withoutLayout: true,
    },
  },
  {
    element: <CsvTable />,
    path: '/reservations/detail',
    title: 'Réservations',
    meta: { withoutLayout: true },
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
    title: 'Page indisponible',
    meta: {
      public: true,
      withoutLayout: true,
    },
  },
  {
    element: <Homepage />,
    path: '/accueil',
    title: 'Accueil',
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
    title: 'Réservations',
    meta: { shouldRedirect: true },
  },
  {
    element: <CollectiveBookings />,
    path: '/reservations/collectives',
    title: 'Réservations',
    meta: { shouldRedirect: true },
  },
  {
    element: <SignIn />,
    path: '/connexion',
    title: 'Connexion',
    meta: {
      public: true,
      withoutLayout: true,
    },
  },
  {
    element: <EmailChangeValidation />,
    path: '/email_validation',
    title: 'Validation changement adresse e-mail',
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
    title: 'Vos structures juridiques',
  },
  {
    element: <OffererDetails />,
    path: '/structures/:offererId',
    title: 'Vos structures juridiques',
    meta: { shouldRedirect: true },
  },
  {
    element: <VenueCreation />,
    path: '/structures/:offererId/lieux/creation',
    title: 'Création d’un lieu',
    meta: { shouldRedirect: true },
  },
  {
    element: <VenueEdition />,
    path: '/structures/:offererId/lieux/:venueId',
    title: 'Edition d’un lieu',
    meta: { shouldRedirect: true },
  },
  {
    element: <CollectiveDataEdition />,
    path: '/structures/:offererId/lieux/:venueId/eac',
    title: 'Mes informations pour les enseignants',
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
    title: 'Vos offres',
    meta: { shouldRedirect: true },
  },
  {
    element: <CollectiveOffers />,
    path: '/offres/collectives',
    title: 'Vos offres collectives',
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
    title: 'Edition d’une offre collective',
    meta: { shouldRedirect: true },
  },
  {
    element: <CollectiveOfferCreation />,
    path: '/offre/creation/collectif',
    title: 'Edition d’une offre collective',
    meta: { shouldRedirect: true },
  },
  {
    element: <CollectiveOfferCreation />,
    path: '/offre/creation/collectif/vitrine',
    title: 'Edition d’une offre collective',
    meta: { shouldRedirect: true },
  },
  {
    element: <CollectiveOfferCreation />,
    path: '/offre/collectif/:offerId/creation',
    title: 'Edition d’une offre collective',
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
    title: 'Edition d’une offre collective',
    meta: { shouldRedirect: true },
  },
  {
    element: <CollectiveOfferSummaryCreation />,
    path: '/offre/:offerId/collectif/creation/recapitulatif',
    title: 'Edition d’une offre collective',
    meta: { shouldRedirect: true },
  },
  {
    element: <CollectiveOfferSummaryCreation />,
    path: '/offre/:offerId/collectif/vitrine/creation/recapitulatif',
    title: 'Edition d’une offre collective',
    meta: { shouldRedirect: true },
  },
  {
    element: <CollectiveOfferConfirmation />,
    path: '/offre/:offerId/collectif/confirmation',
    title: 'Edition d’une offre collective',
    meta: { shouldRedirect: true },
  },
  {
    element: <CollectiveOfferConfirmation />,
    path: '/offre/:offerId/collectif/vitrine/confirmation',
    title: 'Edition d’une offre collective',
    meta: { shouldRedirect: true },
  },
  {
    element: <CollectiveOfferEdition />,
    path: '/offre/:offerId/collectif/edition',
    title: 'Edition d’une offre collective',
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
    title: 'Edition d’une offre collective',
    meta: { shouldRedirect: true },
  },
  {
    element: <CollectiveOfferVisibility />,
    path: '/offre/:offerId/collectif/visibilite/edition',
    title: 'Edition d’une offre collective',
    meta: { shouldRedirect: true },
  },
  {
    element: <ResetPassword />,
    path: '/mot-de-passe-perdu',
    title: 'Mot de passe perdu',
    meta: {
      public: true,
      withoutLayout: true,
    },
  },
  {
    element: <LostPassword />,
    path: '/demande-mot-de-passe',
    title: 'Demande de mot de passe',
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
    title: 'Vos remboursements',
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
