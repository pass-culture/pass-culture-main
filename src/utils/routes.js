import React from 'react'

import BetaPage from '../pages/BetaPage'
import BookingsPage from '../pages/BookingsPage'
import DiscoveryPage from '../pages/DiscoveryPage'
import FavoritesPage from '../pages/FavoritesPage'
import HomePage from '../pages/HomePage'
import InventoryPage from '../pages/InventoryPage'
import OffererPage from '../pages/OffererPage'
import ProfessionalPage from '../pages/ProfessionalPage'
import ProfilePage from '../pages/ProfilePage'
import RedirectToDiscoveryPage from '../pages/RedirectToDiscoveryPage'
import SigninPage from '../pages/SigninPage'
import SignupPage from '../pages/SignupPage'

export const getDiscoveryPath = (offer, mediation='') => {
  const offerId = (typeof offer === 'string') ? offer : offer.id;
  const mediationId = (typeof mediation === 'string') ? mediation : (typeof mediation === 'object' ? mediation.id : '');
  return `/decouverte/${offerId}/${mediationId}`;
}

const routes = [
  {
    exact: true,
    path: '/',
    render: () => <HomePage />
  },
  {
    exact: true,
    path: '/beta',
    render: () => <BetaPage />
  },
  {
    exact: true,
    path: '/connexion',
    render: () => <SigninPage />
  },
  {
    exact: true,
    path: '/decouverte',
    render: () => <RedirectToDiscoveryPage />
  },
  {
    exact: true,
    path: '/decouverte/:offerId/:mediationId?',
    render: ({ match: { mediationId, offerId }}) =>
      <DiscoveryPage mediationId={mediationId} offerId={offerId}/>
  },
  {
    exact: true,
    path: '/favoris',
    render: () => <FavoritesPage />
  },
  {
    exact: true,
    path: '/inscription',
    render: () => <SignupPage />
  },
  {
    exact: true,
    path: '/inventaire',
    render: () => <InventoryPage />
  },
  {
    exact: true,
    path: '/pro',
    render: () => <ProfessionalPage />
  },
  {
    exact: true,
    path:'/pro/:offererId',
    render: props => <OffererPage offererId={props.match.params.offererId} />
  },
  {
    exact: true,
    path: '/profil',
    render: () => <ProfilePage />
  },
  {
    exact: true,
    path: '/reservations',
    render: () => <BookingsPage />
  }
]

export default routes
