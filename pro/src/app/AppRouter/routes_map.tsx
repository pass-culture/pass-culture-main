/* No need to test this file */
/* istanbul ignore file */
import { Navigate, useLocation } from 'react-router-dom-v5-compat'

import AdageIframe from 'pages/AdageIframe/AdageIframe'
import Bookings from 'pages/Bookings'
import CollectiveBookings from 'pages/CollectiveBookings'
import CollectiveOfferConfirmation from 'pages/CollectiveOfferConfirmation'
import CollectiveOfferCreation from 'pages/CollectiveOfferCreation'
import CollectiveOfferEdition from 'pages/CollectiveOfferEdition'
import CollectiveOffers from 'pages/CollectiveOffers'
import CollectiveOfferStockCreation from 'pages/CollectiveOfferStockCreation'
import CollectiveOfferStockEdition from 'pages/CollectiveOfferStockEdition'
import CollectiveOfferSummaryCreation from 'pages/CollectiveOfferSummaryCreation'
import CollectiveOfferSummaryEdition from 'pages/CollectiveOfferSummaryEdition'
import CollectiveOfferVisibilityCreation from 'pages/CollectiveOfferVisibility/CollectiveOfferCreationVisibility'
import CollectiveOfferVisibility from 'pages/CollectiveOfferVisibility/CollectiveOfferEditionVisibility'
import CsvTable from 'pages/CsvTable'
import Desk from 'pages/Desk'
import { EmailChangeValidation } from 'pages/EmailChangeValidation'
import Unavailable from 'pages/Errors/Unavailable/Unavailable'
import Homepage from 'pages/Home/Homepage'
import { Logout } from 'pages/Logout'
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
import { SignupJourneyRoutes } from 'pages/SignupJourneyRoutes'
import { UserProfile } from 'pages/User'
import { VenueCreation } from 'pages/VenueCreation'
import { VenueEdition } from 'pages/VenueEdition'
import CollectiveOfferSelectionDuplication from 'screens/CollectiveOfferSelectionDuplication'
import { UNAVAILABLE_ERROR_PAGE } from 'utils/routes'

export interface ILayoutConfig {
  backTo?: { path: string; label: string } | null
  pageName?: string
  fullscreen?: boolean
}

interface IRouteMeta {
  public?: boolean
  layoutConfig?: ILayoutConfig
}

export interface IRoute {
  component: any
  path: string
  title?: string
  meta?: IRouteMeta
  featureName?: string
  disabledFeatureName?: string
}

const RedirectToConnexionComponent = () => {
  const location = useLocation()
  return <Navigate to={`/connexion${location.search}`} />
}

export const routesWithoutLayout: IRoute[] = [
  {
    component: RedirectToConnexionComponent,
    path: '/',
  },
  {
    component: Logout,
    path: '/logout',
  },
  {
    component: AdageIframe,
    path: '/adage-iframe',
    meta: {
      public: true,
    },
  },
  {
    component: Signup,
    path: '/inscription',
    title: 'Inscription',
    meta: {
      public: true,
    },
  },
  {
    component: Signup,
    path: '/inscription/*',
    title: 'Inscription',
    meta: {
      public: true,
    },
  },
  {
    component: CsvTable,
    path: '/reservations/detail',
    title: 'Réservations',
  },
  {
    component: CsvTable,
    path: '/remboursements-details',
    title: 'Remboursements',
  },
  {
    component: Unavailable,
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
    path: '/accueil',
    title: 'Accueil',
  },
  {
    component: Desk,
    path: '/guichet',
    title: 'Guichet',
  },
  {
    component: Bookings,
    path: '/reservations',
    title: 'Réservations',
  },
  {
    component: CollectiveBookings,
    path: '/reservations/collectives',
    title: 'Réservations',
  },
  {
    component: SetPassword,
    path: '/creation-de-mot-de-passe',
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
    component: SetPassword,
    path: '/creation-de-mot-de-passe/:token',
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
    path: '/creation-de-mot-de-passe-confirmation',
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
    component: SetPasswordConfirm,
    path: '/creation-de-mot-de-passe-erreur',
    title: 'Erreur de création de mot de passe',
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
    path: '/structures',
    title: 'Structures',
  },
  {
    component: OffererCreation,
    path: '/structures/creation',
    title: 'Structures',
  },
  {
    component: OffererDetails,
    path: '/structures/:offererId',
    title: 'Structures',
  },
  {
    component: VenueCreation,
    path: '/structures/:offererId/lieux/creation',
    title: 'Structures',
  },
  {
    component: VenueEdition,
    path: '/structures/:offererId/lieux/:venueId',
    title: 'Structures',
  },
  {
    component: CollectiveDataEdition,
    path: '/structures/:offererId/lieux/:venueId/eac',
    title: 'Structures',
  },
  {
    component: OfferType,
    path: '/offre/creation',
    title: 'Selection du type d’offre',
  },
  {
    component: OffersRoute,
    path: '/offres',
    title: 'Offres',
  },
  {
    component: CollectiveOffers,
    path: '/offres/collectives',
    title: 'Offres',
  },
  {
    component: CollectiveOfferSelectionDuplication,
    path: '/offre/creation/collectif/selection',
    title: 'Edition d’une offre collective',
  },
  {
    component: CollectiveOfferStockCreation,
    path: '/offre/:offerId/collectif/stocks',
    title: 'Edition d’une offre collective',
  },
  {
    component: CollectiveOfferCreation,
    path: '/offre/creation/collectif',
    title: 'Edition d’une offre collective',
  },
  {
    component: CollectiveOfferCreation,
    path: '/offre/creation/collectif/vitrine',
    title: 'Edition d’une offre collective',
  },
  {
    component: CollectiveOfferCreation,
    path: '/offre/collectif/:offerId/creation',
    title: 'Edition d’une offre collective',
  },
  {
    component: CollectiveOfferCreation,
    path: '/offre/collectif/vitrine/:offerId/creation',
    title: 'Edition d’une offre collective',
  },
  {
    component: CollectiveOfferVisibilityCreation,
    path: '/offre/:offerId/collectif/visibilite',
    title: 'Edition d’une offre collective',
  },
  {
    component: CollectiveOfferSummaryCreation,
    path: '/offre/:offerId/collectif/creation/recapitulatif',
    title: 'Edition d’une offre collective',
  },
  {
    component: CollectiveOfferSummaryCreation,
    path: '/offre/:offerId/collectif/vitrine/creation/recapitulatif',
    title: 'Edition d’une offre collective',
  },
  {
    component: CollectiveOfferConfirmation,
    path: '/offre/:offerId/collectif/confirmation',
    title: 'Edition d’une offre collective',
  },
  {
    component: CollectiveOfferConfirmation,
    path: '/offre/:offerId/collectif/vitrine/confirmation',
    title: 'Edition d’une offre collective',
  },
  {
    component: CollectiveOfferEdition,
    path: '/offre/:offerId/collectif/edition',
    title: 'Edition d’une offre collective',
  },
  {
    component: CollectiveOfferSummaryEdition,
    path: '/offre/:offerId/collectif/recapitulatif',
    title: 'Edition d’une offre collective',
  },
  {
    component: CollectiveOfferStockEdition,
    path: '/offre/:offerId/collectif/stocks/edition',
    title: 'Edition d’une offre collective',
  },
  {
    component: CollectiveOfferVisibility,
    path: '/offre/:offerId/collectif/visibilite/edition',
    title: 'Edition d’une offre collective',
  },
  {
    component: LostPassword,
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
    path: '/offre/individuelle/:offerId/*',
    title: 'Offre étape par étape',
  },
  {
    component: Reimbursements,
    path: '/remboursements/*',
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
  {
    component: SignupJourneyRoutes,
    path: '/parcours-inscription/*',
    title: 'Parcours de souscription',
    featureName: 'WIP_ENABLE_NEW_ONBOARDING',
  },
]

export default routes
