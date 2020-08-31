import { IcoNavBookings } from '../layout/NavBar/Icons/IcoNavBookings'
import { IcoNavDebug } from '../layout/NavBar/Icons/IcoNavDebug'
import { IcoNavDiscovery } from '../layout/NavBar/Icons/IcoNavDiscovery'
import { IcoNavFavorites } from '../layout/NavBar/Icons/IcoNavFavorites'
import { IcoNavIdCheck } from '../layout/NavBar/Icons/IcoNavIdCheck'
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
import TutorialsContainer from '../pages/tutorials/TutorialsContainer'
import TypeFormContainer from '../pages/typeform/TypeformContainer'
import EligibilityCheck from '../pages/create-account/EligibilityCheck'
import Debug from '../pages/debug/DebugPage'

import {
  IS_DEBUG_PAGE_ACTIVE,
  IS_HOME_PAGE_ACTIVE,
  IS_ID_CHECK_PAGE_ACTIVE,
} from '../../utils/config'
import HomeContainer from '../pages/home/HomeContainer'
import { IcoNavHome } from '../layout/NavBar/Icons/IcoNavHome'

let routes = [
  {
    component: BetaPageContainer,
    exact: true,
    path: '/',
  },
  {
    component: BetaPageContainer,
    exact: true,
    path: '/beta',
    title: 'Bienvenue dans l’avant-première du pass Culture',
  },
  {
    component: ActivationContainer,
    path: '/activation',
    title: 'Activation',
  },
  {
    component: SignInContainer,
    exact: true,
    path: '/connexion',
    title: 'Connexion',
  },
  {
    component: SignupContainer,
    exact: true,
    featureName: 'WEBAPP_SIGNUP',
    path: '/inscription',
    title: 'Inscription',
  },
  {
    component: EligibilityCheck,
    exact: true,
    path: '/verification-eligibilite',
    title: 'Eligibilité',
  },
  {
    component: TutorialsContainer,
    exact: true,
    path: '/bienvenue',
    title: 'Bienvenue',
  },
  {
    component: ForgotPassword,
    path: '/mot-de-passe-perdu',
    title: 'Mot de passe perdu',
  },
  {
    component: TypeFormContainer,
    exact: true,
    path: '/typeform',
    title: 'Questionnaire',
  },
  {
    component: OfferContainer,
    path: '/offre/:details(details|transition)/:offerId([A-Z0-9]+)/:mediationId(vide|[A-Z0-9]+)?',
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
    path: '/decouverte/:offerId([A-Z0-9]+)?/:mediationId([A-Z0-9]+)?',
    title: 'Les offres',
  },
  {
    component: SearchContainer,
    icon: IcoNavSearch,
    to: '/recherche',
    path: '/recherche',
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
    icon: IcoNavBookings,
    to: '/reservations',
    path: '/reservations',
    title: 'Réservations',
  },
  {
    component: MyFavoritesContainer,
    icon: IcoNavFavorites,
    to: '/favoris',
    path: '/favoris',
    title: 'Favoris',
  },
  {
    component: ProfileContainer,
    icon: IcoNavProfile,
    to: '/profil',
    path: '/profil',
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
    title: "DEV | Gestion d'erreur",
  })
}

if (IS_ID_CHECK_PAGE_ACTIVE) {
  routes.push({
    component: EligibilityCheck,
    exact: true,
    icon: IcoNavIdCheck,
    to: '/verification-eligibilite',
    path: '/verification-eligibilite',
    title: 'ID Check',
  })
}

if (IS_HOME_PAGE_ACTIVE) {
  const profilPage = routes.find(route => route.path === '/profil')
  const profilPageOutOfNavbar = {
    component: profilPage.component,
    path: profilPage.path,
    title: profilPage.title,
  }
  routes = routes.filter(route => route.path !== '/profil')
  routes.push(profilPageOutOfNavbar)
}

export default routes
