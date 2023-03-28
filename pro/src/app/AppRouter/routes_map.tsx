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
import LostPassword from 'pages/LostPassword/LostPassword'
import OffererDetails from 'pages/Offerers/Offerer/OffererDetails/OffererDetails'
import CollectiveDataEdition from 'pages/Offerers/Offerer/VenueV1/VenueEdition/CollectiveDataEdition'
import OffererCreation from 'pages/Offerers/OffererCreation'
import { OffererStats } from 'pages/OffererStats'
import { OfferIndividualWizard } from 'pages/OfferIndividualWizard'
import { Confirmation } from 'pages/OfferIndividualWizard/Confirmation'
import { Offer } from 'pages/OfferIndividualWizard/Offer'
import { PriceCategories } from 'pages/OfferIndividualWizard/PriceCategories'
import { Stocks } from 'pages/OfferIndividualWizard/Stocks'
import { Summary } from 'pages/OfferIndividualWizard/Summary'
import OffersRoute from 'pages/Offers'
import OfferType from 'pages/OfferType'
import Reimbursements from 'pages/Reimbursements'
import SignIn from 'pages/SignIn/SignIn'
import Signup from 'pages/Signup/Signup'
import SignupConfirmation from 'pages/Signup/SignupConfirmation/SignupConfirmation'
import SignupContainer from 'pages/Signup/SignupContainer/SignupContainer'
import SignUpValidation from 'pages/Signup/SignUpValidation'
import { SignupJourneyRoutes } from 'pages/SignupJourneyRoutes'
import { UserProfile } from 'pages/User'
import { VenueCreation } from 'pages/VenueCreation'
import { VenueEdition } from 'pages/VenueEdition'
import CollectiveOfferSelectionDuplication from 'screens/CollectiveOfferSelectionDuplication'
import { Activity } from 'screens/SignupJourneyForm/Activity'
import { OffererAuthentication } from 'screens/SignupJourneyForm/Authentication'
import { ConfirmedAttachment } from 'screens/SignupJourneyForm/ConfirmedAttachment'
import { Offerer } from 'screens/SignupJourneyForm/Offerer'
import { Offerers as SignupJourneyOfferers } from 'screens/SignupJourneyForm/Offerers'
import { Validation } from 'screens/SignupJourneyForm/Validation'
import { Welcome } from 'screens/SignupJourneyForm/Welcome'
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

export interface RouteDefinition {
  parentPath?: string
  path: string
  title?: string
}

export interface IRoute extends RouteDefinition {
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
  },
  {
    element: <CollectiveBookings />,
    path: '/reservations/collectives',
    title: 'Réservations',
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
  },
  {
    element: <OfferType />,
    path: '/offre/creation',
    title: 'Selection du type d’offre',
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
  },
  {
    element: <CollectiveOfferCreation />,
    path: '/offre/creation/collectif',
    title: 'Edition d’une offre collective',
  },
  {
    element: <CollectiveOfferCreation />,
    path: '/offre/creation/collectif/vitrine',
    title: 'Edition d’une offre collective',
  },
  {
    element: <CollectiveOfferCreation />,
    path: '/offre/collectif/:offerId/creation',
    title: 'Edition d’une offre collective',
  },
  {
    element: <CollectiveOfferCreation />,
    path: '/offre/collectif/vitrine/:offerId/creation',
    title: 'Edition d’une offre collective',
  },
  {
    element: <CollectiveOfferVisibilityCreation />,
    path: '/offre/:offerId/collectif/visibilite',
    title: 'Edition d’une offre collective',
  },
  {
    element: <CollectiveOfferSummaryCreation />,
    path: '/offre/:offerId/collectif/creation/recapitulatif',
    title: 'Edition d’une offre collective',
  },
  {
    element: <CollectiveOfferSummaryCreation />,
    path: '/offre/:offerId/collectif/vitrine/creation/recapitulatif',
    title: 'Edition d’une offre collective',
  },
  {
    element: <CollectiveOfferConfirmation />,
    path: '/offre/:offerId/collectif/confirmation',
    title: 'Edition d’une offre collective',
  },
  {
    element: <CollectiveOfferConfirmation />,
    path: '/offre/:offerId/collectif/vitrine/confirmation',
    title: 'Edition d’une offre collective',
  },
  {
    element: <CollectiveOfferEdition />,
    path: '/offre/:offerId/collectif/edition',
    title: 'Edition d’une offre collective',
  },
  {
    element: <CollectiveOfferSummaryEdition />,
    path: '/offre/:offerId/collectif/recapitulatif',
    title: 'Edition d’une offre collective',
  },
  {
    element: <CollectiveOfferStockEdition />,
    path: '/offre/:offerId/collectif/stocks/edition',
    title: 'Edition d’une offre collective',
  },
  {
    element: <CollectiveOfferVisibility />,
    path: '/offre/:offerId/collectif/visibilite/edition',
    title: 'Edition d’une offre collective',
  },
  {
    element: <LostPassword />,
    path: '/mot-de-passe-perdu',
    title: 'Mot de passe perdu',
    meta: {
      public: true,
      withoutLayout: true,
    },
  },
  {
    element: <OfferIndividualWizard />,
    path: '/offre/individuelle/:offerId/*',
    title: 'Offre étape par étape',
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

export const routesOfferIndividualWizard: IRoute[] = [
  {
    element: <Offer />,
    parentPath: '/offre/individuelle/:offerId',
    path: '/informations',
    title: 'Détails de l’offre',
  },
  {
    element: <Offer />,
    parentPath: '/offre/individuelle/:offerId',
    path: '/creation/informations',
    title: 'Détails de l’offre',
  },
  {
    element: <Offer />,
    parentPath: '/offre/individuelle/:offerId',
    path: '/brouillon/informations',
    title: 'Détails de l’offre',
  },
  {
    element: <PriceCategories />,
    parentPath: '/offre/individuelle/:offerId',
    path: '/creation/tarifs',
    title: 'Vos tarifs',
  },
  {
    element: <PriceCategories />,
    parentPath: '/offre/individuelle/:offerId',
    path: '/brouillon/tarifs',
    title: 'Vos tarifs',
  },
  {
    element: <PriceCategories />,
    parentPath: '/offre/individuelle/:offerId',
    path: '/tarifs',
    title: 'Vos tarifs',
  },
  {
    element: <Stocks />,
    parentPath: '/offre/individuelle/:offerId',
    path: '/creation/stocks',
    title: 'Vos stocks',
  },
  {
    element: <Stocks />,
    parentPath: '/offre/individuelle/:offerId',
    path: '/brouillon/stocks',
    title: 'Vos stocks',
  },
  {
    element: <Stocks />,
    parentPath: '/offre/individuelle/:offerId',
    path: '/stocks',
    title: 'Vos stocks',
  },
  {
    element: <Summary />,
    parentPath: '/offre/individuelle/:offerId',
    path: '/creation/recapitulatif',
    title: 'Récapitulatif',
  },
  {
    element: <Summary />,
    parentPath: '/offre/individuelle/:offerId',
    path: '/brouillon/recapitulatif',
    title: 'Récapitulatif',
  },
  {
    element: <Summary />,
    parentPath: '/offre/individuelle/:offerId',
    path: '/recapitulatif',
    title: 'Récapitulatif',
  },
  {
    element: <Confirmation />,
    parentPath: '/offre/individuelle/:offerId',
    path: '/creation/confirmation',
    title: 'Confirmation',
  },
  {
    element: <Confirmation />,
    parentPath: '/offre/individuelle/:offerId',
    path: '/brouillon/confirmation',
    title: 'Confirmation',
  },
  {
    element: <Confirmation />,
    parentPath: '/offre/individuelle/:offerId',
    path: '/confirmation',
    title: 'Confirmation',
  },
]

export const routesSignup: IRoute[] = [
  {
    element: <SignupContainer />,
    parentPath: '/inscription',
    path: '/',
    title: 'S’inscrire',
  },
  {
    element: <SignupConfirmation />,
    parentPath: '/inscription',
    path: '/confirmation',
    title: 'S’inscrire',
  },
  {
    element: <SignUpValidation />,
    parentPath: '/inscription',
    path: '/validation/:token',
    title: 'S’inscrire',
  },
]

export const routesSignupJourney: IRoute[] = [
  {
    element: <Welcome />,
    parentPath: '/parcours-inscription',
    path: '/',
    title: '',
  },
  {
    element: <Offerer />,
    parentPath: '/parcours-inscription',
    path: '/structure',
    title: '',
  },
  {
    element: <SignupJourneyOfferers />,
    parentPath: '/parcours-inscription',
    path: '/structure/rattachement',
    title: '',
  },
  {
    element: <ConfirmedAttachment />,
    parentPath: '/parcours-inscription',
    path: '/structure/rattachement/confirmation',
    title: '',
  },
  {
    element: <OffererAuthentication />,
    parentPath: '/parcours-inscription',
    path: '/authentification',
    title: '',
  },
  {
    element: <OffererAuthentication />,
    parentPath: '/parcours-inscription',
    path: '/authentification',
    title: '',
  },
  {
    element: <Activity />,
    parentPath: '/parcours-inscription',
    path: '/activite',
    title: '',
  },
  {
    element: <Validation />,
    parentPath: '/parcours-inscription',
    path: '/validation',
    title: '',
  },
]

export const routesDefinitions: RouteDefinition[] = [
  ...routes,
  ...routesOfferIndividualWizard,
  ...routesSignup,
  ...routesSignupJourney,
].map(({ path, parentPath, title }) => {
  return { path, parentPath, title }
})

export default routes
