import React from 'react'
import { Redirect } from 'react-router'

import AccoutingPage from '../components/pages/AccountingPage'
import DeskPage from '../components/pages/DeskPage'
import HomePage from '../components/pages/HomePage'
import MediationPage from '../components/pages/MediationPage'
import OffersPage from '../components/pages/OffersPage'
import OfferPage from '../components/pages/OfferPage'
import OffererPage from '../components/pages/OffererPage'
import OfferersPage from '../components/pages/OfferersPage'
import ProfilePage from '../components/pages/ProfilePage'
import SigninPage from '../components/pages/SigninPage'
import SignupPage from '../components/pages/SignupPage'
import TermsPage from '../components/pages/TermsPage'
import VenuePage from '../components/pages/VenuePage'
import LostPasswordPage from '../components/pages/LostPasswordPage'

// NOTE: routes are sorted by PATH alphabetical order
const routes = [
  {
    path: '/',
    render: () => <Redirect to="/connexion" />,
  },
  {
    component: HomePage,
    path: '/accueil',
    title: 'Accueil',
  },
  {
    component: AccoutingPage,
    path: '/comptabilite',
    title: 'Comptabilité',
  },
  {
    component: SigninPage,
    path: '/connexion',
    title: 'Connexion',
  },
  {
    component: DeskPage,
    path: '/guichet',
    title: 'Guichet',
  },
  {
    component: SignupPage,
    path: '/inscription',
    title: 'Inscription',
  },
  {
    component: TermsPage,
    path: '/mentions-legales',
    title: 'Mentions Légales',
  },
  {
    component: LostPasswordPage,
    path: '/mot-de-passe-perdu',
    title: 'Mot de passe perdu',
  },
  {
    component: OfferersPage,
    path: '/structures',
    title: 'Structures',
  },
  {
    component: OffererPage,
    path: '/structures/:offererId',
    title: 'Structure',
  },
  {
    component: VenuePage,
    path: '/structures/:offererId/lieux/:venueId',
    title: 'Lieu',
  },
  {
    component: VenuePage,
    path: '/structures/:offererId/lieux/:venueId/fournisseurs/:venueProviderId',
    title: 'Lieu',
  },
  {
    component: OffersPage,
    path: '/structures/:offererId/lieux/:venueId/offres',
    title: 'Offres',
  },
  {
    component: OffersPage,
    path: '/offres',
    title: 'Offres',
  },
  {
    component: OfferPage,
    path: '/offres/:offerId',
    title: 'Offre',
  },
  {
    component: MediationPage,
    path: '/offres/:offerId/accroches/:mediationId',
    title: 'Accroche',
  },
  {
    component: OfferPage,
    path: '/structures/:offererId/offres/:offerId',
    title: 'Offres',
  },
  {
    component: OfferPage,
    path: '/structures/:offererId/lieux/:venueId/offres/:offerId',
    title: 'Offres',
  },
  {
    component: ProfilePage,
    path: '/profil',
    title: 'Profil',
  },
]

export default routes
