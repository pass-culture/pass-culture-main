/* No need to test this file */
/* istanbul ignore file */
import { Redirect, useLocation } from 'react-router-dom'

import Bookings from 'pages/Bookings'
import CollectiveBookings from 'pages/CollectiveBookings'
import CollectiveOfferRoutes from 'pages/CollectiveOfferRoutes'
import CollectiveOffers from 'pages/CollectiveOffers'
import CsvTable from 'pages/CsvTable'
import Desk from 'pages/Desk'
import { EmailChangeValidation } from 'pages/EmailChangeValidation'
import Unavailable from 'pages/Errors/Unavailable/Unavailable'
import Homepage from 'pages/Home/Homepage'
import LostPassword from 'pages/LostPassword/LostPassword'
import Offerers from 'pages/Offerers/List/Offerers'
import OffererDetails from 'pages/Offerers/Offerer/OffererDetails/OffererDetails'
import CollectiveDataEdition from 'pages/Offerers/Offerer/VenueV1/VenueEdition/CollectiveDataEdition'
import OffererCreation from 'pages/Offerers/OffererCreation'
import { OffererStats } from 'pages/OffererStats'
import { OfferIndividualWizard } from 'pages/OfferIndividualWizard'
import OffersRoute from 'pages/Offers'
import OfferType from 'pages/OfferType'
import Reimbursements from 'pages/Reimbursements'
import SetPassword from 'pages/SetPassword/SetPassword'
import SetPasswordConfirm from 'pages/SetPasswordConfirm/SetPasswordConfirm'
import SignIn from 'pages/SignIn/SignIn'
import Signup from 'pages/Signup/Signup'
import SignUpValidation from 'pages/SignUpValidation'
import { UserProfile } from 'pages/User'
import { VenueCreation } from 'pages/VenueCreation'
import { VenueEdition } from 'pages/VenueEdition'
import { UNAVAILABLE_ERROR_PAGE } from 'utils/routes'

interface ILayoutConfig {
  pageName?: string
  fullscreen?: boolean
}

interface IRouteMeta {
  public?: boolean
  layoutConfig?: ILayoutConfig
}

export interface IRoute {
  component: any
  exact?: boolean
  path: string | string[]
  title?: string
  meta?: IRouteMeta
  featureName?: string
  disabledFeatureName?: string
}

const RedirectToConnexionComponent = () => {
  const location = useLocation()
  return <Redirect to={`/connexion${location.search}`} />
}

export const routesWithoutLayout: IRoute[] = [
  {
    component: RedirectToConnexionComponent,
    exact: true,
    path: '/',
  },
  {
    component: Signup,
    exact: true,
    path: '/inscription/(confirmation)?',
    title: 'Inscription',
    meta: {
      public: true,
    },
  },
  {
    component: SignUpValidation,
    exact: true,
    path: '/inscription/validation/:token',
    title: 'Validation de votre inscription',
    meta: {
      public: true,
    },
  },
  {
    component: CsvTable,
    exact: true,
    path: '/reservations/detail',
    title: 'Réservations',
  },
  {
    component: CsvTable,
    exact: true,
    path: '/remboursements-details',
    title: 'Liste de vos remboursements',
  },
  {
    component: Unavailable,
    exact: true,
    path: UNAVAILABLE_ERROR_PAGE,
    title: 'Page indisponible',
    meta: {
      public: true,
    },
  },
]

// Routes wrapped with app layout
const routes: IRoute[] = [
  {
    component: Homepage,
    exact: true,
    path: '/accueil',
    title: 'Espace acteurs culturels',
  },
  {
    component: Desk,
    exact: true,
    path: '/guichet',
    title: 'Guichet',
  },
  {
    component: Bookings,
    exact: true,
    path: '/reservations',
    title: 'Vos réservations',
  },
  {
    component: CollectiveBookings,
    exact: true,
    path: '/reservations/collectives',
    title: 'Vos réservations d’offres collectives',
  },
  {
    component: SetPassword,
    exact: true,
    path: ['/creation-de-mot-de-passe/:token?'],
    title: 'Définition du mot de passe',
    meta: {
      public: true,
      layoutConfig: {
        fullscreen: true,
        pageName: 'sign-in',
      },
    },
  },
  {
    component: SetPasswordConfirm,
    exact: true,
    path: ['/creation-de-mot-de-passe-confirmation'],
    title: 'Confirmation du mot de passe',
    meta: {
      public: true,
      layoutConfig: {
        fullscreen: true,
        pageName: 'sign-in',
      },
    },
  },
  {
    component: SignIn,
    exact: true,
    path: '/connexion',
    title: 'Se connecter',
    meta: {
      public: true,
      layoutConfig: {
        fullscreen: true,
        pageName: 'sign-in',
      },
    },
  },
  {
    component: EmailChangeValidation,
    path: '/email_validation',
    title: 'Validation changement adresse e-mail',
    meta: {
      public: true,
      layoutConfig: {
        fullscreen: true,
        pageName: 'sign-in',
      },
    },
  },
  {
    component: Offerers,
    exact: true,
    path: '/structures',
    title: 'Vos structures juridiques',
  },
  {
    component: OffererCreation,
    exact: true,
    path: '/structures/creation',
    title: 'Créer une structure',
  },
  {
    component: OffererDetails,
    exact: true,
    path: '/structures/:offererId([A-Z0-9]+)',
    title: 'Détails de votre structure',
  },
  {
    component: VenueCreation,
    exact: true,
    path: '/structures/:offererId([A-Z0-9]+)/lieux/creation',
    title: 'Structures',
  },
  {
    component: VenueEdition,
    exact: true,
    path: '/structures/:offererId([A-Z0-9]+)/lieux/:venueId([A-Z0-9]+)',
    title: 'Structures',
  },

  {
    component: CollectiveDataEdition,
    exact: true,
    path: '/structures/:offererId([A-Z0-9]+)/lieux/:venueId([A-Z0-9]+)/eac',
    title: 'Structures',
  },
  {
    component: OfferType,
    exact: true,
    path: '/offre/creation',
    title: 'Selection du type d’offre',
  },
  {
    component: OffersRoute,
    exact: true,
    path: '/offres',
    title: 'Vos offres',
  },
  {
    component: CollectiveOffers,
    exact: true,
    path: '/offres/collectives',
    title: 'Vos offres collectives',
  },
  {
    component: CollectiveOfferRoutes,
    exact: false,
    path: [
      '/offre/:offerId/collectif',
      '/offre/creation/collectif',
      '/offre/collectif/:offerId/creation',
      '/offre/collectif/vitrine/:offerId/creation',
    ],
    title: 'Edition d’une offre collective',
  },
  {
    component: LostPassword,
    exact: true,
    path: '/mot-de-passe-perdu',
    title: 'Mot de passe perdu',
    meta: {
      public: true,
      layoutConfig: {
        fullscreen: true,
        pageName: 'sign-in',
      },
    },
  },
  {
    component: OfferIndividualWizard,
    exact: false,
    path: ['/offre/individuelle/:offerId'],
    title: 'Offre étape par étape',
  },
  {
    component: Reimbursements,
    path: '/remboursements',
    title: 'Vos remboursements',
    meta: {
      layoutConfig: {
        pageName: 'reimbursements',
      },
    },
  },
  {
    component: UserProfile,
    path: '/profil',
    title: 'Profil',
  },
  {
    component: OffererStats,
    path: '/statistiques',
    title: 'Statistiques',
    featureName: 'ENABLE_OFFERER_STATS',
  },
]

export const routeNotFound = {
  path: '*',
  title: 'Page inaccessible',
}

const offerPath = '/offre/individuelle/:offerId'
export const subRoutesOfferIndividualWizard = [
  {
    path: [
      `${offerPath}/creation/informations`,
      `${offerPath}/brouillon/informations`,
      `${offerPath}/informations`,
    ],
    title: 'Détails de l’offre',
  },
  {
    path: [
      `${offerPath}/creation/tarifs`,
      `${offerPath}/brouillon/tarifs`,
      `${offerPath}/tarifs`,
    ],
    title: 'Vos tarifs',
  },
  {
    path: [
      `${offerPath}/creation/stocks`,
      `${offerPath}/brouillon/stocks`,
      `${offerPath}/stocks`,
    ],
    title: 'Vos stocks',
  },
  {
    path: [
      `${offerPath}/creation/recapitulatif`,
      `${offerPath}/brouillon/recapitulatif`,
      `${offerPath}/recapitulatif`,
    ],
    title: 'Récapitulatif',
  },
  {
    path: [
      `${offerPath}/creation/confirmation`,
      `${offerPath}/brouillon/confirmation`,
      `${offerPath}/confirmation`,
    ],
    title: 'Confirmation',
  },
]

export const subRoutesInscription = [
  { path: '/inscription', title: 'S’inscrire' },
]

export const subRoutesCollectiveOfferEdition = [
  { path: '/offre/:offerId/collectif/edition', title: 'Détails de l’offre' },
  {
    path: '/offre/:offerId/collectif/recapitulatif',
    title: 'Récapitulatif',
  },
  {
    path: '/offre/:offerId/collectif/stocks/edition',
    title: 'Vos Stocks',
  },
  {
    path: '/offre/:offerId/collectif/visibilite/edition',
    title: 'Visibilité',
  },
]

export const subRoutesCollectiveOfferEdition2 = [
  { path: '/offre/creation/collectif/vitrine', title: 'Détails de l’offre' },
  {
    path: '/offre/creation/collectif',
    title: 'Détails de l’offre',
  },
  {
    path: '/offre/collectif/vitrine/:offerId/creation',
    title: 'Vos Stocks',
  },
  {
    path: '/offre/:offerId/collectif/stocks',
    title: 'Vos Stocks',
  },
  {
    path: '/offre/:offerId/collectif/visibilite',
    title: 'Visibilité',
  },
  {
    path: [
      '/offre/:offerId/collectif/creation/recapitulatif',
      '/offre/:offerId/collectif/vitrine/creation/recapitulatif',
    ],
    title: 'Récapitulatif',
  },
  {
    path: [
      '/offre/:offerId/collectif/confirmation',
      '/offre/:offerId/collectif/vitrine/confirmation',
    ],
    title: 'Confirmation',
  },
]

export default routes
