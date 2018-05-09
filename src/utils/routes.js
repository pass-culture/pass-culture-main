import React from 'react'
import { Redirect } from 'react-router'

import BetaPage from '../components/pages/BetaPage'
import ManagementPage from '../components/pages/ManagementPage'
import ModifyOffererPage from '../components/pages/ModifyOffererPage'
import ModifyOfferPage from '../components/pages/ModifyOfferPage'
import OfferPage from '../components/pages/OfferPage'
import OffererPage from '../components/pages/OffererPage'
import ProfilePage from '../components/pages/ProfilePage'
import SettingsPage from '../components/pages/SettingsPage'
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
    path: '/gestion',
    title: 'Gestion',
    render: () => <ManagementPage />,
  },
  {
    exact: true,
    path: '/gestion/:offererId',
    title: 'Gestion',
    render: props => <OffererPage offererId={props.match.params.offererId} />,
  },
  {
    exact: true,
    path: '/gestion/:offererId/espace',
    title: 'Gestion',
    render: props => <ModifyOffererPage  />,
  },
  {
    exact: true,
    path: '/gestion/:offererId/:offerId',
    title: 'Gestion',
    render: props => <OfferPage
      offererId={props.match.params.offererId}
      offerId={props.match.params.offerId}
    />,
  },
  {
    exact: true,
    path: '/inscription',
    title: 'Inscription',
    render: () => <SignupPage />,
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
    exact: true,
    path: '/reglages',
    title: 'Réglages',
    render: () => <SettingsPage />,
  },
]

export default routes
