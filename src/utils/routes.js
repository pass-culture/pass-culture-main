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
    path: '/',
    render: () => <Redirect to="/beta" />,
  },
  {
    component: BetaPage,
    path: '/beta',
    title: "Bienvenue dans l'avant-première du Pass Culture",
  },
  {
    component: SigninPage,
    path: '/connexion',
    title: 'Connexion',
  },
  {
    component: SignupPage,
    path: '/inscription',
    title: 'Inscription',
  },
  {
    component: DiscoveryPage,
    path: '/decouverte',
    subroutes: ['/decouverte/:offerId/:mediationId?'],
    title: 'Les offres',
  },
  {
    component: FavoritesPage,
    path: '/favoris',
    title: 'Mes favoris',
  },
  {
    component: InventoryPage,
    path: '/inventaire',
    title: 'Inventaire',
  },
  {
    component: ProfilePage,
    path: '/profil',
    title: 'Profil',
  },
  {
    component: BookingsPage,
    path: '/reservations',
    title: 'Réservations',
  },
  {
    component: TermsPage,
    path: '/mentions-legales',
    title: 'Mentions Légales',
  },
]

export default routes
