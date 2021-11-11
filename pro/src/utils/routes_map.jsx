import React from 'react'
import { Redirect } from 'react-router'

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
import { UNAVAILABLE_ERROR_PAGE } from 'utils/routes'

const RedirectToConnexionComponent = () => <Redirect to="/connexion" />

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
    exact: true,
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
    path: '/remboursements/detail',
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
    component: OfferLayoutContainer,
    exact: false,
    path: ['/offres/creation', '/offres/:offerId([A-Z0-9]+)'],
    title: 'Offre',
  },
  {
    component: Offers,
    exact: true,
    path: '/offres',
    title: 'Offres',
  },
]

export default routes
