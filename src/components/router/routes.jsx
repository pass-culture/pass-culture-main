import React from 'react'
import { Redirect } from 'react-router-dom'

import ActivationRoutesContainer from '../pages/activation/ActivationRoutesContainer'
import BetaPage from '../pages/BetaPage'
import MyBookingsContainer from '../pages/my-bookings/MyBookingsContainer'
import DiscoveryContainer from '../pages/discovery/DiscoveryContainer'
import FavoritesPage from '../pages/FavoritesPage'
import ForgotPasswordPage from '../pages/ForgotPasswordPage'
import ProfilePage from '../pages/profile'
import TypeFormPage from '../pages/typeform/TypeFormContainer'
import SearchContainer from '../pages/search/SearchContainer'
import SigninContainer from '../pages/signin/SigninContainer'
import SignupContainer from '../pages/signup/SignupContainer'
import { WEBAPP_CONTACT_EXTERNAL_PAGE } from '../../utils/config'

function redirectToBeta () {
  return <Redirect to="/beta" />
}

const routes = [
  {
    path: '/',
    render: redirectToBeta,
  },
  {
    component: BetaPage,
    path: '/beta',
    title: 'Bienvenue dans l’avant-première du pass Culture',
  },
  {
    component: ActivationRoutesContainer,
    path: '/activation/:token?',
    title: 'Activation',
  },
  {
    component: SigninContainer,
    path: '/connexion',
    title: 'Connexion',
  },
  {
    component: SignupContainer,
    featureName: 'WEBAPP_SIGNUP',
    path: '/inscription',
    title: 'Inscription',
  },
  {
    component: ForgotPasswordPage,
    path: '/mot-de-passe-perdu/:view?',
    title: 'Mot de passe perdu',
  },
  {
    component: TypeFormPage,
    path: '/typeform',
    title: 'Questionnaire',
  },
  /* ---------------------------------------------------
   *
   * MENU ITEMS
   * NOTE les elements ci-dessous sont les elements du main menu
   * Car ils contiennent une propriété `icon`
   *
   ---------------------------------------------------  */
  {
    component: DiscoveryContainer,
    icon: 'offres-w',
    // exemple d'URL optimale qui peut être partagée
    // par les sous composants
    path:
      '/decouverte/:offerId?/:mediationId?/:view(booking|verso)?/:bookingId?/:view(cancelled)?',
    title: 'Les offres',
  },
  {
    component: SearchContainer,
    icon: 'search-w',
    path:
      '/recherche/(resultats)?/:option?/:subOption?/:offerId?/:mediationIdOrView?/:view(booking)?/:bookingId?',
    title: 'Recherche',
  },
  {
    component: MyBookingsContainer,
    icon: 'calendar-w',
    path: '/reservations',
    title: 'Mes réservations',
  },
  {
    component: FavoritesPage,
    featureName: 'FAVORITE_OFFER',
    icon: 'like-w',
    path: '/favoris',
    title: 'Mes préférés',
  },
  {
    component: ProfilePage,
    icon: 'user-w',
    path: '/profil/:view?/:status?',
    title: 'Mon compte',
  },
  {
    href: WEBAPP_CONTACT_EXTERNAL_PAGE,
    icon: 'help-w',
    target: '_blank',
    title: 'Aide',
  },
  {
    href:
      'https://pass-culture.gitbook.io/documents/textes-normatifs/mentions-legales-et-conditions-generales-dutilisation-de-lapplication-pass-culture',
    icon: 'txt-w',
    target: '_blank',
    title: 'Mentions légales',
  },
]

export default routes
