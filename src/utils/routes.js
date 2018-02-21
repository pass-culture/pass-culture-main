import React from 'react'

import ActivitiesPage from '../pages/ActivitiesPage'
import ClientOfferPage from '../pages/ClientOfferPage'
import DiscoveryPage from '../pages/DiscoveryPage'
import InventoryPage from '../pages/InventoryPage'
import HomePage from '../pages/HomePage'
import OffererPage from '../pages/OffererPage'
import ProfessionalPage from '../pages/ProfessionalPage'
import ProfilePage from '../pages/ProfilePage'
import SignPage from '../pages/SignPage'

const routes = [
  {
    exact: true,
    path: '/',
    render: () => <HomePage />
  },
  {
    exact: true,
    path: '/activities',
    render: () => <ActivitiesPage />
  },
  {
    exact: true,
    path: '/decouverte',
    render: () => <DiscoveryPage />
  },
  {
    exact: true,
    path: '/decouverte/:offerId',
    render: props => <ClientOfferPage offerId={props.match.params.offerId} />
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
    path: '/inscription',
    render: () => <SignPage />
  },
  {
    exact: true,
    path: '/inventaire',
    render: () => <InventoryPage />
  },
  {
    exact: true,
    path: '/profile',
    render: () => <ProfilePage />
  }
]

export default routes
