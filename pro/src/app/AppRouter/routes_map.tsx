/* No need to test this file */
/* istanbul ignore file */
import { Redirect, useLocation } from 'react-router-dom'

import Bookings from 'pages/Bookings'
import BusinessUnitList from 'pages/BusinessUnitList'
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
import VenueV1Creation from 'pages/Offerers/Offerer/VenueV1/VenueCreation/VenueCreation'
import CollectiveDataEdition from 'pages/Offerers/Offerer/VenueV1/VenueEdition/CollectiveDataEdition'
import VenueV1Edition from 'pages/Offerers/Offerer/VenueV1/VenueEdition/VenueEdition'
import OffererCreation from 'pages/Offerers/OffererCreation'
import { OffererStats } from 'pages/OffererStats'
import { OfferIndividualWizard } from 'pages/OfferIndividualWizard'
import OffersRoute from 'pages/Offers'
import OfferLayout from 'pages/Offers/Offer/OfferLayout'
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
    title: 'Remboursements',
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
    title: 'Accueil',
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
    title: 'Réservations',
  },
  {
    component: CollectiveBookings,
    exact: true,
    path: '/reservations/collectives',
    title: 'Réservations',
  },
  {
    component: SetPassword,
    exact: true,
    path: ['/creation-de-mot-de-passe/:token?'],
    title: 'Création de mot de passe',
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
    title: 'Confirmation création de mot de passe',
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
    title: 'Connexion',
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
    title: 'Structures',
  },
  {
    component: OffererCreation,
    exact: true,
    path: '/structures/creation',
    title: 'Structures',
  },
  {
    component: OffererDetails,
    exact: true,
    path: '/structures/:offererId([A-Z0-9]+)',
    title: 'Structures',
  },
  {
    component: VenueV1Creation,
    exact: true,
    path: '/structures/:offererId([A-Z0-9]+)/lieux/creation',
    title: 'Structures',
    disabledFeatureName: 'VENUE_FORM_V2',
  },
  {
    component: VenueV1Edition,
    exact: true,
    path: '/structures/:offererId([A-Z0-9]+)/lieux/:venueId([A-Z0-9]+)',
    title: 'Structures',
    disabledFeatureName: 'VENUE_FORM_V2',
  },
  {
    component: VenueCreation,
    exact: true,
    path: '/structures/:offererId([A-Z0-9]+)/lieux/creation',
    title: 'Structures',
    featureName: 'VENUE_FORM_V2',
  },
  {
    component: VenueEdition,
    exact: true,
    path: '/structures/:offererId([A-Z0-9]+)/lieux/:venueId([A-Z0-9]+)',
    title: 'Structures',
    featureName: 'VENUE_FORM_V2',
  },

  {
    component: CollectiveDataEdition,
    exact: true,
    path: '/structures/:offererId([A-Z0-9]+)/lieux/:venueId([A-Z0-9]+)/eac',
    title: 'Structures',
  },
  {
    component: BusinessUnitList,
    exact: true,
    path: '/structures/:offererId([A-Z0-9]+)/point-de-remboursement',
    title: 'Structures',
    featureName: 'ENFORCE_BANK_INFORMATION_WITH_SIRET',
  },
  {
    component: OfferType,
    exact: true,
    path: '/offre/creation',
    title: 'Selection du type d’offre',
  },
  {
    component: OfferLayout,
    exact: false,
    path: [
      '/offre/creation/individuel',
      '/offre/:offerId([A-Z0-9]+)/individuel',
    ],
    title: 'Offre',
  },
  {
    component: OffersRoute,
    exact: true,
    path: '/offres',
    title: 'Offres',
  },
  {
    component: CollectiveOffers,
    exact: true,
    path: '/offres/collectives',
    title: 'Offres',
  },
  {
    component: CollectiveOfferRoutes,
    exact: false,
    path: [
      '/offre/:offerId/collectif',
      '/offre/duplication/collectif',
      '/offre/creation/collectif',
      '/offre/collectif/:offerId/creation',
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
    path: ['/offre/v3', '/offre/:offerId/v3'],
    title: 'Offre étape par étape',
    featureName: 'OFFER_FORM_V3',
  },
  {
    component: Reimbursements,
    path: '/remboursements',
    title: 'Remboursements',
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

export default routes
