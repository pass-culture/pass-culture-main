import React from 'react'
import { Redirect } from 'react-router'
import { useLocation } from 'react-router-dom'

import CsvDetailViewContainer from 'components/layout/CsvTable/CsvTableContainer'
import BookingsRecapContainer from 'components/pages/Bookings/BookingsRecapContainer'
import DeskContainer from 'components/pages/Desk/DeskContainer'
import Unavailable from 'components/pages/Errors/Unavailable/Unavailable'
import Homepage from 'components/pages/Home/Homepage'
import LostPasswordContainer from 'components/pages/LostPassword/LostPasswordContainer'
import OfferersLayout from 'components/pages/Offerers/OfferersLayout'
import OfferLayoutContainer from 'components/pages/Offers/Offer/OfferLayoutContainer'
import Offers from 'components/pages/Offers/Offers/OffersContainer'
import ReimbursementsContainer from 'components/pages/Reimbursements/ReimbursementsContainer'
import SetPasswordContainer from 'components/pages/SetPassword/SetPasswordContainer'
import SetPasswordConfirmContainer from 'components/pages/SetPasswordConfirm/SetPasswordConfirmContainer'
import SigninContainer from 'components/pages/Signin/SigninContainer'
import SignupContainer from 'components/pages/Signup/SignupContainer'
import SignupValidationContainer from 'components/pages/Signup/SignupValidation/SignupValidationContainer'
import StyleguideContainer from 'components/pages/Styleguide/StyleguideContainer'
import OfferEducationalConfirmation from 'routes/OfferEducationalConfirmation'
import OfferEducationalCreation from 'routes/OfferEducationalCreation'
import OfferEducationalEdition from 'routes/OfferEducationalEdition'
import OfferEducationalStockCreation from 'routes/OfferEducationalStockCreation'
import OfferEducationalStockEdition from 'routes/OfferEducationalStockEdition/OfferEducationalStockEdition'
import OfferType from 'routes/OfferType'
import { UNAVAILABLE_ERROR_PAGE } from 'utils/routes'

const RedirectToConnexionComponent = () => {
  const location = useLocation()
  return <Redirect to={`/connexion${location.search}`} />
}

// NOTE: routes are sorted by PATH alphabetical order
// DEPRECATED: Pages are currently be rework to not use <Main> component
export const routesWithMain = [
  {
    component: RedirectToConnexionComponent,
    exact: true,
    path: '/',
  },
  {
    component: SigninContainer,
    exact: true,
    path: '/connexion',
    title: 'Connexion',
    meta: {
      public: true,
    },
  },
  {
    component: DeskContainer,
    exact: true,
    path: '/guichet',
    title: 'Guichet',
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
    component: SignupValidationContainer,
    exact: true,
    path: '/inscription/validation/:token',
    title: 'Validation de votre inscription',
    meta: {
      public: true,
    },
  },
  {
    component: LostPasswordContainer,
    exact: true,
    path: '/mot-de-passe-perdu',
    title: 'Mot de passe perdu',
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

// Routes that does not use <Main> and are now functional components
const routes = [
  {
    component: Homepage,
    exact: true,
    path: '/accueil',
    title: 'Accueil',
  },
  {
    component: BookingsRecapContainer,
    exact: true,
    path: '/reservations',
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
    component: OfferEducationalStockEdition,
    exact: true,
    path: '/offre/:offerId([A-Z0-9]+)/collectif/stocks/edition',
    title: 'Edition d’un stock d’une offre scolaire',
  },
]

export default routes
