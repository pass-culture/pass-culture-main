import React from 'react'
import { Redirect } from 'react-router'

import AccoutingPage from '../components/pages/AccountingPage'
import HomePage from '../components/pages/HomePage'
import MediationPage from '../components/pages/MediationPage'
import MediationsPage from '../components/pages/MediationsPage'
import NotFoundPage from '../components/pages/NotFoundPage'
import OccasionsPage from '../components/pages/OccasionsPage'
import OccasionPage from '../components/pages/OccasionPage'
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
    render: () => <Redirect to="/connexion" />,
  },
  {
    exact: true,
    path: '/comptabilite',
    title: "Comptabilité",
    render: () => <AccoutingPage />,
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
    path: '/structures/:offererId/lieux/:venueId/fournisseurs/:venueProviderId',
    title: 'Lieu',
    render: () => <VenuePage />,
  },
  {
    exact: true,
    path: '/structures/:offererId/lieux/:venueId/offres',
    title: 'Offres',
    render: () => <OccasionsPage />,
  },
  {
    exact: true,
    path: '/offres',
    title: 'Offres',
    render: () => <OccasionsPage />,
  },
  {
    exact: true,
    path: '/offres/:occasionId',
    title: 'Offre',
    render: () => <OccasionPage />,
  },
  {
    exact: true,
    path: '/offres/:occasionId/:feature',
    title: 'Offre',
    render: () => <OccasionPage />,
  },
  {
    exact: true,
    path: '/offres/:occasionId/:feature/:eventOccurenceId',
    title: 'Offre',
    render: () => <OccasionPage />,
  },
  {
    exact: true,
    path: '/structures/:offererId/offres/:occasionId',
    title: 'Offres',
    render: () => <OccasionPage />,
  },
  {
    exact: true,
    path: '/structures/:offererId/lieux/:venueId/offres/:occasionId',
    title: 'Offres',
    render: () => <OccasionPage />,
  },
  {
    exact: true,
    path: '/offres/:occasionId/accroches/:mediationId',
    title: 'Accroche',
    render: () => <MediationPage />,
  },
  {
    exact: true,
    path: '/offres/:occasionId/accroches',
    title: 'Accroches',
    render: () => <MediationsPage />,
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
  },
  {
    title: 'Page non trouvée',
    render: () => <NotFoundPage />,
  }
]

export default routes
