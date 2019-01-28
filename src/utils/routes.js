import React from 'react'
import { Redirect } from 'react-router-dom'

import ActivationPage from '../components/pages/activation'
import BetaPage from '../components/pages/BetaPage'
import MyBookingsPage from '../components/pages/my-bookings'
import DiscoveryPage from '../components/pages/discovery'
import FavoritesPage from '../components/pages/FavoritesPage'
import ForgotPasswordPage from '../components/pages/ForgotPasswordPage'
import ProfilePage from '../components/pages/profile'
import SearchPage from '../components/pages/SearchPage'
import { Signin } from '../components/pages/signin'
import SignupPage from '../components/pages/SignupPage'
import TermsPage from '../components/pages/TermsPage'

// NOTE: la gestion des éléments du menu principal
// se fait dans le fichier src/components/MainMenu
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
    component: ActivationPage,
    path: '/activation/:token?/:view?',
    title: 'Activation',
  },
  {
    component: Signin,
    path: '/connexion',
    title: 'Connexion',
  },
  {
    component: SignupPage,
    path: '/inscription',
    title: 'Inscription',
  },
  {
    component: ForgotPasswordPage,
    path: '/mot-de-passe-perdu/:view?',
    title: 'Mot de passe perdu',
  },
  /* ---------------------------------------------------
   *
   * MENU ITEMS
   * NOTE les elements ci-dessous sont les elements du main menu
   * Car ils contiennent une propriété `icon`
   *
   ---------------------------------------------------  */
  {
    component: DiscoveryPage,
    disabled: false,
    icon: 'offres-w',
    // exemple d'URL optimale qui peut être partagée
    // par les sous composants
    path:
      '/decouverte/:offerId?/:mediationId?/:view(booking|verso|cancelled)?/:bookingId?',
    title: 'Les offres',
  },
  {
    component: SearchPage,
    disabled: false,
    icon: 'search-w',
    path: '/recherche/:view(resultats)?/:categorie?',
    title: 'Recherche',
  },
  {
    component: MyBookingsPage,
    disabled: false,
    icon: 'calendar-w',
    path: '/reservations',
    title: 'Mes Réservations',
  },
  {
    component: FavoritesPage,
    disabled: true,
    icon: 'like-w',
    path: '/favoris',
    title: 'Mes Préférés',
  },
  {
    component: ProfilePage,
    disabled: false,
    icon: 'user-w',
    path: '/profil/:view?/:status?',
    title: 'Mon Profil',
  },
  {
    disabled: false,
    href: 'mailto:pass@culture.gouv.fr',
    icon: 'mail-w',
    title: 'Nous contacter',
  },
  {
    component: TermsPage,
    disabled: false,
    icon: 'txt-w',
    path: '/mentions-legales',
    title: 'Mentions Légales',
  },
]

export default routes
