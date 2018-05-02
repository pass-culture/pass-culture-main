import React from 'react'
import { Redirect } from 'react-router'

import BetaPage from '../components/pages/BetaPage'
import OffererPage from '../components/pages/OffererPage'
import ProfessionalPage from '../components/pages/ProfessionalPage'
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
    path: '/gestion',
    title: 'Espace pro',
    render: () => <ProfessionalPage />,
  },
  {
    exact: true,
    path: '/gestion/:offererId',
    title: 'Espace pro - Offre',
    render: props => <OffererPage offererId={props.match.params.offererId} />,
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
]

export default routes
