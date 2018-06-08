import React from 'react'
import { Redirect } from 'react-router'

import AccoutingPage from '../components/pages/AccountingPage'
import BetaPage from '../components/pages/BetaPage'
import HomePage from '../components/pages/HomePage'
import MediationPage from '../components/pages/MediationPage'
import MediationsPage from '../components/pages/MediationsPage'
import OffersPage from '../components/pages/OffersPage'
import OfferPage from '../components/pages/OfferPage'
import OffererPage from '../components/pages/OffererPage'
import OfferersPage from '../components/pages/OfferersPage'
import ProfilePage from '../components/pages/ProfilePage'
import SigninPage from '../components/pages/SigninPage'
import SignupPage from '../components/pages/SignupPage'
import TermsPage from '../components/pages/TermsPage'
import VenuePage from '../components/pages/VenuePage'

const routes = [
  {
    exact: true,
    path: '/',
    render: () => <Redirect to="/beta" />,
  },
  {
    exact: true,
    path: '/comptabilite',
    title: "Comptabilité",
    render: () => <AccoutingPage />,
  },
  {
    exact: true,
    path: '/beta',
    title: "Bienvenue dans l'avant-première du Pass Culture",
    render: () => <BetaPage />,
  },
  {
    exact: true,
    path: '/connexion',
    title: 'Connexion',
    render: () => <SigninPage />,
  },
  {
    exact: true,
    path: '/inscription',
    title: 'Inscription',
    render: () => <SignupPage />,
  },
  {
    exact: true,
    path: '/accueil',
    title: 'Accueil',
    render: () => <HomePage />,
  },
  {
    exact: true,
    path: '/structures',
    title: 'Structures',
    render: () => <OfferersPage />,
  },
  {
    exact: true,
    path: '/structures/:offererId',
    title: 'Structure',
    render: () => <OffererPage />,
  },
  {
    exact: true,
    path: '/structures/:offererId/lieux/:venueId',
    title: 'Lieu',
    render: () => <VenuePage />,
  },
  {
    exact: true,
    path: '/structures/:offererId/lieux/:venueId/fournisseurs/nouveau',
    title: 'Lieu',
    render: () => <VenuePage />,
  },
  {
    exact: true,
    path: '/structures/:offererId/lieux/:venueId/offres',
    title: 'Offres',
    render: () => <OffersPage />,
  },
  {
    exact: true,
    path: '/offres',
    title: 'Offres',
    render: () => <OffersPage />,
  },
  {
    exact: true,
    path: '/offres/:occasionPath',
    render: () => <Redirect to="/offres" />,
  },
  {
    exact: true,
    path: '/offres/:occasionPath/:occasionId',
    title: 'Offre',
    render: () => <OfferPage />,
  },
  {
    exact: true,
    path: '/offres/:occasionPath/:occasionId/accroches',
    title: 'Accroches',
    render: props => <MediationsPage />,
  },
  {
    exact: true,
    path: '/offres/:occasionPath/:occasionId/accroches/:mediationId',
    title: 'Accroche',
    render: props => <MediationPage />,
  },
  {
    exact: true,
    path: '/profil',
    title: 'Profil',
    render: () => <ProfilePage />,
  },
  {
    exact: true,
    path: '/mentions-legales',
    title: 'Mentions Légales',
    render: () => <TermsPage />,
  }
]

export default routes
