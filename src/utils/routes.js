import React from 'react'
import { Redirect } from 'react-router'

import BetaPage from '../pages/BetaPage'
import BookingsPage from '../pages/BookingsPage'
import DiscoveryPage from '../pages/DiscoveryPage'
import FavoritesPage from '../pages/FavoritesPage'
import InventoryPage from '../pages/InventoryPage'
import OffererPage from '../pages/OffererPage'
import ProfessionalPage from '../pages/ProfessionalPage'
import ProfilePage from '../pages/ProfilePage'
import SigninPage from '../pages/SigninPage'
import SignupPage from '../pages/SignupPage'

export const getDiscoveryPath = (offer, mediation='') => {
  const offerId = (typeof offer === 'string')
    ? offer
    : (typeof offer === 'object' ? offer.id : 'tuto');
  const mediationId = (typeof mediation === 'string')
    ? mediation
    : (typeof mediation === 'object' ? mediation.id : '');
  return `/decouverte/${offerId}/${mediationId}`;
}

const routes = [
  {
    exact: true,
    path: '/',
    render: () => <Redirect to='/beta' />
  },
  {
    exact: true,
    path: '/beta',
    title: 'Bienvenue dans l\'avant-première du Pass Culture',
    render: () => <BetaPage />
  },
  {
    exact: true,
    path: '/connexion',
    title: 'Connexion',
    render: () => <SigninPage />
  },
  {
    exact: true,
    path: '/inscription',
    title: 'Inscription',
    render: () => <SignupPage />
  },
  {
    exact: true,
    path: '/decouverte',
    render: () => <Redirect to='/decouverte/empty' />
  },
  {
    exact: true,
    path: '/decouverte/:offerId/:mediationId?',
    title: 'Les offres',
    render: ({ match: { params: { mediationId, offerId } } }) =>
      <DiscoveryPage mediationId={mediationId} offerId={offerId}/>
  },
  {
    exact: true,
    path: '/favoris',
    title: 'Mes favoris',
    render: () => <FavoritesPage />
  },
  {
    exact: true,
    path: '/inventaire',
    title: 'Inventaire',
    render: () => <InventoryPage />
  },
  {
    exact: true,
    path: '/pro',
    title: 'Espace pro',
    render: () => <ProfessionalPage />
  },
  {
    exact: true,
    path:'/pro/:offererId',
    title: 'Espace pro - Offre',
    render: props => <OffererPage offererId={props.match.params.offererId} />
  },
  {
    exact: true,
    path: '/profil',
    title: 'Profil',
    render: () => <ProfilePage />
  },
  {
    exact: true,
    path: '/reservations',
    title: 'Réservations',
    render: () => <BookingsPage />
  }
]

export default routes
