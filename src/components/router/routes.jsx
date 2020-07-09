import React from 'react'
import { Redirect } from 'react-router-dom'

import { IcoNavBookings } from '../layout/NavBar/Icons/IcoNavBookings'
import { IcoNavDebug } from '../layout/NavBar/Icons/IcoNavDebug'
import { IcoNavDiscovery } from '../layout/NavBar/Icons/IcoNavDiscovery'
import { IcoNavFavorites } from '../layout/NavBar/Icons/IcoNavFavorites'
import { IcoNavProfile } from '../layout/NavBar/Icons/IcoNavProfile'
import { IcoNavSearch } from '../layout/NavBar/Icons/IcoNavSearch'
import ActivationContainer from '../pages/activation/ActivationContainer'
import BetaPageContainer from '../pages/beta-page/BetaPageContainer'
import MyBookingsContainer from '../pages/my-bookings/MyBookingsContainer'
import DiscoveryContainer from '../pages/discovery/DiscoveryContainer'
import MyFavoritesContainer from '../pages/my-favorites/MyFavoritesContainer'
import ForgotPassword from '../pages/forgot-password/ForgotPassword'
import OfferContainer from '../pages/offer/OfferContainer'
import ProfileContainer from '../pages/profile/ProfileContainer'
import SignupContainer from '../pages/signup/SignupContainer'
import SearchContainer from '../pages/search/SearchContainer'
import SignInContainer from '../pages/signin/SignInContainer'
import CreateAccount from '../pages/create-account/CreateAccount'
import TutorialsContainer from '../pages/tutorials/TutorialsContainer'
import TypeFormContainer from '../pages/typeform/TypeformContainer'
import Debug from '../pages/debug/DebugPage'

import { IS_DEBUG_PAGE_ACTIVE } from '../../utils/config'
import HomeContainer from '../pages/home/HomeContainer'
import { IcoNavHome } from '../layout/NavBar/Icons/IcoNavHome'

function redirectToBeta() {
  return <Redirect to="/beta" />
}

const routes = [
  {
    exact: true,
    path: '/',
    render: redirectToBeta,
    sensitive: true,
  },
  {
    component: BetaPageContainer,
    exact: true,
    path: '/beta',
    sensitive: true,
    title: 'Bienvenue dans l’avant-première du pass Culture',
  },
  {
    component: ActivationContainer,
    exact: true,
    path: '/activation/:token([A-Z0-9]+|error|lien-invalide)',
    sensitive: true,
    title: 'Activation',
  },
  {
    component: SignInContainer,
    exact: true,
    path: '/connexion',
    sensitive: true,
    title: 'Connexion',
  },
  {
    component: SignupContainer,
    exact: true,
    featureName: 'WEBAPP_SIGNUP',
    path: '/inscription',
    sensitive: true,
    title: 'Inscription',
  },
  {
    component: CreateAccount,
    exact: true,
    path:
      '/verification-eligibilite' +
      '/(eligible|departement-non-eligible|pas-eligible|bientot|trop-tot|gardons-contact)?',
    sensitive: true,
    title: 'Eligibilité',
  },
  {
    component: TutorialsContainer,
    exact: true,
    path: '/bienvenue',
    sensitive: true,
    title: 'Bienvenue',
  },
  {
    component: ForgotPassword,
    exact: true,
    path: '/mot-de-passe-perdu/(succes)?',
    sensitive: true,
    title: 'Mot de passe perdu',
  },
  {
    component: TypeFormContainer,
    exact: true,
    path: '/typeform',
    sensitive: true,
    title: 'Questionnaire',
  },
  {
    component: OfferContainer,
    exact: true,
    path:
      '/offre' +
      '/:details(details|transition)?' +
      '/:offerId([A-Z0-9]+)?' +
      '/:mediationId(vide|[A-Z0-9]+)?' +
      '/:booking(reservation)?' +
      '/:bookingId([A-Z0-9]+)?' +
      '/:cancellation(annulation)?' +
      '/:confirmation(confirmation)?',
    sensitive: true,
    title: 'Détail de l’offre',
  },
  /* ---------------------------------------------------
   *
   * NAVBAR ITEMS
   * NOTE les elements ci-dessous sont les elements de la navbar
   * Car ils contiennent une propriété `icon`
   *
   ---------------------------------------------------  */
  {
    component: DiscoveryContainer,
    exact: true,
    icon: IcoNavDiscovery,
    to: '/decouverte',
    path:
      '/decouverte' +
      '/:offerId([A-Z0-9]+)?' +
      '/:mediationId([A-Z0-9]+)?' +
      '/:details(details|transition)?' +
      '/:booking(reservation)?' +
      '/:bookingId([A-Z0-9]+)?' +
      '/:cancellation(annulation)?' +
      '/:confirmation(confirmation)?',
    sensitive: true,
    title: 'Les offres',
  },
  {
    component: SearchContainer,
    exact: true,
    featureName: 'SEARCH_ALGOLIA',
    icon: IcoNavSearch,
    to: '/recherche',
    path:
      '/recherche' +
      '/(resultats|criteres-localisation/place|criteres-localisation|criteres-categorie|criteres-tri)?' +
      '/(filtres|tri)?' +
      '/(localisation|localisation/place)?' +
      '/:details(details|transition)?' +
      '/:offerId([A-Z0-9]+)?' +
      '/:mediationId(vide|[A-Z0-9]+)?' +
      '/:booking(reservation)?' +
      '/:bookingId([A-Z0-9]+)?' +
      '/:cancellation(annulation)?' +
      '/:confirmation(confirmation)?',
    sensitive: true,
    title: 'Recherche',
  },
  {
    component: HomeContainer,
    featureName: 'WEBAPP_HOMEPAGE',
    icon: IcoNavHome,
    path: '/accueil',
    to: '/accueil',
    title: 'Accueil',
  },
  {
    component: MyBookingsContainer,
    exact: true,
    icon: IcoNavBookings,
    to: '/reservations',
    path:
      '/reservations' +
      '/:details(details|transition)?' +
      '/:bookingId([A-Z0-9]+)?' +
      '/:booking(reservation)?' +
      '/:cancellation(annulation)?' +
      '/:confirmation(confirmation)?' +
      '/:qrcode(qrcode)?',
    sensitive: true,
    title: 'Réservations',
  },
  {
    component: MyFavoritesContainer,
    exact: true,
    icon: IcoNavFavorites,
    to: '/favoris',
    path:
      '/favoris' +
      '/:details(details|transition)?' +
      '/:offerId([A-Z0-9]+)?' +
      '/:mediationId(vide|[A-Z0-9]+)?' +
      '/:booking(reservation)?' +
      '/:bookingId([A-Z0-9]+)?' +
      '/:cancellation(annulation)?' +
      '/:confirmation(confirmation)?',
    sensitive: true,
    title: 'Favoris',
  },
  {
    component: ProfileContainer,
    exact: true,
    icon: IcoNavProfile,
    to: '/profil',
    path: '/profil/:view(mot-de-passe|informations|mentions-legales)?',
    sensitive: true,
    title: 'Mon compte',
  },
]

if (IS_DEBUG_PAGE_ACTIVE) {
  routes.push({
    component: Debug,
    exact: true,
    icon: IcoNavDebug,
    to: '/errors',
    path: '/errors',
    sensitive: true,
    title: "DEV | Gestion d'erreur",
  })
}

export default routes
