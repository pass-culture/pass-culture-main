import { IS_DEBUG_PAGE_ACTIVE } from '../../utils/config'
import { IcoNavBookings } from '../layout/NavBar/Icons/IcoNavBookings'
import { IcoNavDebug } from '../layout/NavBar/Icons/IcoNavDebug'
import { IcoNavFavorites } from '../layout/NavBar/Icons/IcoNavFavorites'
import { IcoNavHome } from '../layout/NavBar/Icons/IcoNavHome'
import { IcoNavProfile } from '../layout/NavBar/Icons/IcoNavProfile'
import { IcoNavSearch } from '../layout/NavBar/Icons/IcoNavSearch'
import ActivationContainer from '../pages/activation/ActivationContainer'
import BetaPageContainer from '../pages/beta-page/BetaPageContainer'
import Debug from '../pages/debug/DebugPage'
import ForgotPassword from '../pages/forgot-password/ForgotPassword'
import HomeContainer from '../pages/home/HomeContainer'
import MyBookingsContainer from '../pages/my-bookings/MyBookingsContainer'
import MyFavoritesContainer from '../pages/my-favorites/MyFavoritesContainer'
import OfferContainer from '../pages/offer/OfferContainer'
import ProfileContainer from '../pages/profile/ProfileContainer'
import SearchContainer from '../pages/search/SearchContainer'
import SignInContainer from '../pages/signin/SignInContainer'
import SignupContainer from '../pages/signup/SignupContainer'
import TutorialsContainer from '../pages/tutorials/TutorialsContainer'
import TypeFormContainer from '../pages/typeform/TypeformContainer'
import DiscoveryRedirectionToHome from '../pages/discovery/DiscoveryRedirectionToHome'
import EmailChange from '../pages/email-change/EmailChange'
import SignUpFromNativeApp from '../pages/create-account/SignUpFromNativeApp/SignUpFromNativeApp'

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
    component: SignUpFromNativeApp,
    exact: true,
    path: '/verification-eligibilite',
    title: "Télécharge l'application",
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
    component: EmailChange,
    path: '/changement-email',
    title: "Changement d'email",
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
  {
    component: DiscoveryRedirectionToHome,
    path: '/decouverte/:offerId([A-Z0-9]+)?/:mediationId([A-Z0-9]+)?',
    title: 'Les offres',
  },
  /* ---------------------------------------------------
   *
   * NAVBAR ITEMS
   * NOTE les elements ci-dessous sont les elements de la navbar
   * Car ils contiennent une propriété `icon`
   *
   ---------------------------------------------------  */
  {
    component: HomeContainer,
    featureName: 'WEBAPP_HOMEPAGE',
    icon: IcoNavHome,
    path: '/accueil',
    to: '/accueil',
    title: 'Accueil',
  },
  {
    component: SearchContainer,
    icon: IcoNavSearch,
    to: '/recherche',
    path: '/recherche',
    title: 'Recherche',
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

export default routes
