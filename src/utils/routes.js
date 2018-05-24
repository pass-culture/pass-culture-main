import React from 'react'
import { Redirect } from 'react-router'

import BetaPage from '../components/pages/BetaPage'
import HomePage from '../components/pages/HomePage'
import OffersPage from '../components/pages/OffersPage'
import OccasionPage from '../components/pages/OccasionPage'
import OfferersPage from '../components/pages/OfferersPage'
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
    path: '/offres',
    title: 'Offres',
    render: () => <OffersPage />,
  },
  {
    exact: true,
    path: '/occasions/:occasionType/:occasionId',
    title: 'Occasion',
    render: props => <OccasionPage
      occasionId={props.match.params.occasionId}
      occasionType={props.match.params.occasionType}
    />,
  },
  {
    exact: true,
    path: '/mentions-legales',
    title: 'Mentions Légales',
    render: () => <TermsPage />,
  }
]

export default routes
