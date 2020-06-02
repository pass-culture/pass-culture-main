import React from 'react'
import { Redirect } from 'react-router-dom'

import { IcoNavBookings } from '../layout/NavBar/Icons/IcoNavBookings'
import { IcoNavDiscovery } from '../layout/NavBar/Icons/IcoNavDiscovery'
import { IcoNavFavorites } from '../layout/NavBar/Icons/IcoNavFavorites'
import { IcoNavProfile } from '../layout/NavBar/Icons/IcoNavProfile'
import { IcoNavSearch } from '../layout/NavBar/Icons/IcoNavSearch'
import ActivationContainer from '../pages/activation/ActivationContainer'
import BetaPageContainer from '../pages/beta-page/BetaPageContainer'
import DiscoveryContainerV3 from '../pages/discovery-v3/DiscoveryContainer'
import DiscoveryContainer from '../pages/discovery/DiscoveryContainer'
import ForgotPassword from '../pages/forgot-password/ForgotPassword'
import MyBookingsContainer from '../pages/my-bookings/MyBookingsContainer'
import MyFavoritesContainer from '../pages/my-favorites/MyFavoritesContainer'
import OfferContainer from '../pages/offer/OfferContainer'
import ProfileContainer from '../pages/profile/ProfileContainer'
import SearchContainer from '../pages/search/SearchContainer'
import SignInContainer from '../pages/signin/SignInContainer'
import SignupContainer from '../pages/signup/SignupContainer'
import TutorialsContainer from '../pages/tutorials/TutorialsContainer'
import TypeFormContainer from '../pages/typeform/TypeformContainer'

function redirectToBeta() {
  return <Redirect to="/beta" />
}

const routes = [
  {
    path: '/',
    render: redirectToBeta,
  },
  {
    component: BetaPageContainer,
    path: '/beta',
    title: 'Bienvenue dans l’avant-première du pass Culture',
  },
  {
    component: ActivationContainer,
    path: '/activation/:token?',
    title: 'Activation',
  },
  {
    component: SignInContainer,
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
    component: TutorialsContainer,
    path: '/bienvenue',
    title: 'Bienvenue',
  },
  {
    component: ForgotPassword,
    path: '/mot-de-passe-perdu/:view?',
    title: 'Mot de passe perdu',
  },
  {
    component: TypeFormContainer,
    path: '/typeform',
    title: 'Questionnaire',
  },
  {
    component: OfferContainer,
    path:
      '/offre' +
      '/:details(details|transition)?' +
      '/:offerId([A-Z0-9]+)?' +
      '/:mediationId(vide|[A-Z0-9]+)?' +
      '/:booking(reservation)?' +
      '/:bookingId([A-Z0-9]+)?' +
      '/:cancellation(annulation)?' +
      '/:confirmation(confirmation)?',
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
    title: 'Les offres',
  },
  {
    component: SearchContainer,
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
    title: 'Recherche',
  },
  {
    component: MyBookingsContainer,
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
    title: 'Mes réservations',
  },
  {
    component: MyFavoritesContainer,
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
    title: 'Mes favoris',
  },
  {
    component: ProfileContainer,
    icon: IcoNavProfile,
    to: '/profil',
    path: '/profil/:view(mot-de-passe|informations|mentions-legales)?',
    title: 'Mon compte',
  },
  {
    component: DiscoveryContainerV3,
    featureName: 'RECOMMENDATIONS_WITH_GEOLOCATION',
    icon: IcoNavDiscovery,
    to: '/decouverte-v3',
    path:
      '/decouverte-v3' +
      '/:offerId([A-Z0-9]+)?' +
      '/:mediationId([A-Z0-9]+)?' +
      '/:details(details|transition)?' +
      '/:booking(reservation)?/:bookingId([A-Z0-9]+)?' +
      '/:cancellation(annulation)?' +
      '/:confirmation(confirmation)?',
    title: 'Offres géolocalisées',
  },
]

export default routes
