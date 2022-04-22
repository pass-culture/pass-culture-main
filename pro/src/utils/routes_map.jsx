import React from 'react'
import { Redirect } from 'react-router'
import { useLocation } from 'react-router-dom'

import Unavailable from 'components/pages/Errors/Unavailable/Unavailable'
import Homepage from 'components/pages/Home/Homepage'
import LostPassword from 'components/pages/LostPassword/LostPassword'
import OfferersLayout from 'components/pages/Offerers/OfferersLayout'
import OfferLayoutContainer from 'components/pages/Offers/Offer/OfferLayoutContainer'
import ReimbursementsContainer from 'components/pages/Reimbursements/ReimbursementsContainer'
import SetPasswordContainer from 'components/pages/SetPassword/SetPasswordContainer'
import SetPasswordConfirmContainer from 'components/pages/SetPasswordConfirm/SetPasswordConfirmContainer'
import SignIn from 'components/pages/SignIn/SignIn'
import SignupContainer from 'components/pages/Signup/SignupContainer'
import StyleguideContainer from 'components/pages/Styleguide/StyleguideContainer'
import Bookings from 'routes/Bookings'
import CollectiveBookings from 'routes/CollectiveBookings'
import CollectiveOffers from 'routes/CollectiveOffers'
import CsvDetailViewContainer from 'routes/CsvTable'
import Desk from 'routes/Desk'
import OfferEducationalConfirmation from 'routes/OfferEducationalConfirmation'
import OfferEducationalCreation from 'routes/OfferEducationalCreation'
import OfferEducationalEdition from 'routes/OfferEducationalEdition'
import OfferEducationalStockCreation from 'routes/OfferEducationalStockCreation'
import OfferEducationalStockEdition from 'routes/OfferEducationalStockEdition/OfferEducationalStockEdition'
import Offers from 'routes/Offers'
import OfferType from 'routes/OfferType'
import SignUpValidation from 'routes/SignUpValidation'
import { UNAVAILABLE_ERROR_PAGE } from 'utils/routes'

const RedirectToConnexionComponent = () => {
  const location = useLocation()
  return <Redirect to={`/connexion${location.search}`} />
}

export const routesWithoutLayout = [
  {
    component: RedirectToConnexionComponent,
    exact: true,
    path: '/',
  },
  {
    component: SignupContainer,
    exact: true,
    path: '/inscription/(confirmation)?',
    title: 'Inscription',
    meta: {
      public: true,
    },
  },
  {
    component: SignUpValidation,
    exact: true,
    path: '/inscription/validation/:token',
    title: 'Validation de votre inscription',
    meta: {
      public: true,
    },
  },
  {
    component: ReimbursementsContainer,
    path: '/remboursements',
    title: 'Remboursements',
  },
  {
    component: CsvDetailViewContainer,
    exact: true,
    path: '/reservations/detail',
    title: 'Réservations',
  },
  {
    component: CsvDetailViewContainer,
    exact: true,
    path: '/remboursements-details',
    title: 'Remboursements',
  },
  {
    component: StyleguideContainer,
    exact: true,
    path: '/styleguide',
    title: 'Styleguide',
  },
  {
    component: Unavailable,
    exact: true,
    path: UNAVAILABLE_ERROR_PAGE,
    title: 'Page indisponible',
    meta: {
      public: true,
    },
  },
]

// Routes wrapped with app layout
const routes = [
  {
    component: Homepage,
    exact: true,
    path: '/accueil',
    title: 'Accueil',
  },
  {
    component: Desk,
    exact: true,
    path: '/guichet',
    title: 'Guichet',
  },
  {
    component: Bookings,
    exact: true,
    path: '/reservations',
    title: 'Réservations',
  },
  {
    component: CollectiveBookings,
    exact: true,
    path: '/reservations/collectives',
    title: 'Réservations',
  },
  {
    component: SetPasswordContainer,
    exact: true,
    path: ['/creation-de-mot-de-passe/:token?'],
    title: 'Création de mot de passe',
    meta: {
      public: true,
      layoutConfig: {
        fullscreen: true,
        pageName: 'sign-in',
      },
    },
  },
  {
    component: SetPasswordConfirmContainer,
    exact: true,
    path: ['/creation-de-mot-de-passe-confirmation'],
    title: 'Confirmation création de mot de passe',
    meta: {
      public: true,
      layoutConfig: {
        fullscreen: true,
        pageName: 'sign-in',
      },
    },
  },
  {
    component: SignIn,
    exact: true,
    path: '/connexion',
    title: 'Connexion',
    meta: {
      public: true,
      layoutConfig: {
        fullscreen: true,
        pageName: 'sign-in',
      },
    },
  },
  {
    component: OfferersLayout,
    exact: false,
    path: '/structures',
    title: 'Structures',
  },
  {
    component: OfferType,
    exact: true,
    path: '/offre/creation',
    title: 'Selection du type d’offre',
  },
  {
    component: OfferLayoutContainer,
    exact: false,
    path: [
      '/offre/creation/individuel',
      '/offre/:offerId([A-Z0-9]+)/individuel',
    ],
    title: 'Offre',
  },
  {
    component: OfferEducationalCreation,
    exact: true,
    path: '/offre/creation/collectif',
    title: 'Offre Scolaire',
  },
  {
    component: Offers,
    exact: true,
    path: '/offres',
    title: 'Offres',
  },
  {
    component: CollectiveOffers,
    exact: true,
    path: '/offres/collectives',
    title: 'Offres',
    featureName: 'ENABLE_INDIVIDUAL_AND_COLLECTIVE_OFFER_SEPARATION',
  },
  {
    component: OfferEducationalStockCreation,
    exact: true,
    path: '/offre/:offerId([A-Z0-9]+)/collectif/stocks',
    title: 'Stock lié à une offre Scolaire',
  },
  {
    component: OfferEducationalConfirmation,
    exact: true,
    path: '/offre/:offerId([A-Z0-9]+)/collectif/confirmation',
    title: 'Page de confirmation de création d’offre',
  },
  {
    component: OfferEducationalEdition,
    exact: true,
    path: '/offre/:offerId([A-Z0-9]+)/collectif/edition',
    title: 'Edition d’une offre scolaire',
  },
  {
    component: OfferEducationalEdition,
    exact: true,
    path: '/offre/:offerId(T-[A-Z0-9]+)/collectif/edition',
    title: 'Edition d’une offre scolaire',
  },
  {
    component: OfferEducationalStockEdition,
    exact: true,
    path: '/offre/:offerId([A-Z0-9]+)/collectif/stocks/edition',
    title: 'Edition d’un stock d’une offre scolaire',
  },
  {
    component: LostPassword,
    exact: true,
    path: '/mot-de-passe-perdu',
    title: 'Mot de passe perdu',
    meta: {
      public: true,
      layoutConfig: {
        fullscreen: true,
        pageName: 'sign-in',
      },
    },
  },
]

export default routes
