import React from 'react'
import { Redirect } from 'react-router'

import BetaPage from '../components/pages/BetaPage'
import BookingsPage from '../components/pages/BookingsPage'
import DiscoveryPage from '../components/pages/DiscoveryPage'
import FavoritesPage from '../components/pages/FavoritesPage'
import InventoryPage from '../components/pages/InventoryPage'
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
    path: '/beta',
    render: () => <BetaPage />,
    title: "Bienvenue dans l'avant-première du Pass Culture",
  },
  {
    exact: true,
    path: '/connexion',
    render: () => <SigninPage />,
    title: 'Connexion',
  },
  {
    exact: true,
    path: '/inscription',
    render: () => <SignupPage />,
    title: 'Inscription',
  },
  {
    exact: true,
    path: '/decouverte',
    render: () => <DiscoveryPage />,
  },
  {
    exact: true,
    path: '/decouverte/:offerId/:mediationId?',
    render: () => <DiscoveryPage />,
    title: 'Les offres',
  },
  {
    exact: true,
    path: '/favoris',
    render: () => <FavoritesPage />,
    title: 'Mes favoris',
  },
  {
    exact: true,
    path: '/inventaire',
    render: () => <InventoryPage />,
    title: 'Inventaire',
  },
  {
    exact: true,
    path: '/profil',
    render: () => <ProfilePage />,
    title: 'Profil',
  },
  {
    exact: true,
    path: '/reservations',
    render: () => <BookingsPage />,
    title: 'Réservations',
  },
  {
    exact: true,
    path: '/mentions-legales',
    render: () => <TermsPage />,
    title: 'Mentions Légales',
  },
]

export default routes
