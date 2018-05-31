import React from 'react'
import { Redirect } from 'react-router'

import AccoutingPage from '../components/pages/AccountingPage'
import BetaPage from '../components/pages/BetaPage'
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
    path: '/lieux',
    title: 'Lieux',
    render: () => <OfferersPage />,
  },
  {
    exact: true,
    path: '/lieux/:offererId',
    title: 'Lieux',
    render: () => <OffererPage />,
  },
  {
    exact: true,
    path: '/offres',
    title: 'Offres',
    render: () => <OffersPage />,
  },
  {
    exact: true,
    path: '/offres/:occasionPath/:occasionId',
    title: 'Offre',
    render: () => <OfferPage />,
  },
  {
    exact: true,
    path: '/offres/:occasionType/:occasionId/accroches/:mediationId',
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
