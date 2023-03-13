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
  exact?: boolean
  path: string | string[]
  title?: string
  meta?: IRouteMeta
  featureName?: string
  disabledFeatureName?: string
  useV6Router?: boolean
}

const RedirectToConnexionComponent = () => {
  const location = useLocation()
  return <Navigate to={`/connexion${location.search}`} />
}

export const routesWithoutLayout: IRoute[] = [
  {
    component: RedirectToConnexionComponent,
    exact: true,
    path: '/',
    useV6Router: true,
  },
  {
    component: AdageIframe,
    exact: true,
    path: '/adage-iframe',
    meta: {
      public: true,
    },
    useV6Router: true,
  },
  {
    component: Signup,
    exact: true,
    path: '/inscription',
    title: 'Inscription',
    meta: {
      public: true,
    },
    useV6Router: true,
  },
  {
    component: Signup,
    exact: true,
    path: '/inscription/*',
    title: 'Inscription',
    meta: {
      public: true,
    },
    useV6Router: true,
  },
  {
    component: CsvTable,
    exact: true,
    path: '/reservations/detail',
    title: 'Réservations',
    useV6Router: true,
  },
  {
    component: CsvTable,
    exact: true,
    path: '/remboursements-details',
    title: 'Remboursements',
    useV6Router: true,
  },
  {
    component: Unavailable,
    exact: true,
    path: UNAVAILABLE_ERROR_PAGE,
    title: 'Page indisponible',
    meta: {
      public: true,
    },
    useV6Router: true,
  },
]

// Routes wrapped with app layout
const routes: IRoute[] = [
  {
    component: Homepage,
    exact: true,
    path: '/accueil',
    title: 'Accueil',
    useV6Router: true,
  },
  {
    component: Desk,
    exact: true,
    path: '/guichet',
    title: 'Guichet',
    useV6Router: true,
  },
  {
    component: Bookings,
    exact: true,
    path: '/reservations',
    title: 'Réservations',
    useV6Router: true,
  },
  {
    component: CollectiveBookings,
    exact: true,
    path: '/reservations/collectives',
    title: 'Réservations',
    useV6Router: true,
  },
  {
    component: SetPassword,
    exact: true,
    path: '/creation-de-mot-de-passe',
    title: 'Création de mot de passe',
    meta: {
      public: true,
      layoutConfig: {
        fullscreen: true,
        pageName: 'sign-in',
      },
    },
    useV6Router: true,
  },
  {
    component: SetPassword,
    exact: true,
    path: '/creation-de-mot-de-passe/:token',
    title: 'Création de mot de passe',
    meta: {
      public: true,
      layoutConfig: {
        fullscreen: true,
        pageName: 'sign-in',
      },
    },
    useV6Router: true,
  },
  {
    component: SetPasswordConfirm,
    exact: true,
    path: '/creation-de-mot-de-passe-confirmation',
    title: 'Confirmation création de mot de passe',
    meta: {
      public: true,
      layoutConfig: {
        fullscreen: true,
        pageName: 'sign-in',
      },
    },
    useV6Router: true,
  },
  {
    component: SetPasswordConfirm,
    exact: true,
    path: '/creation-de-mot-de-passe-erreur',
    title: 'Erreur de création de mot de passe',
    meta: {
      public: true,
      layoutConfig: {
        fullscreen: true,
        pageName: 'sign-in',
      },
    },
    useV6Router: true,
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
    useV6Router: true,
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
    useV6Router: true,
  },
  {
    component: Offerers,
    exact: true,
    path: '/structures',
    title: 'Structures',
    useV6Router: true,
  },
  {
    component: OffererCreation,
    exact: true,
    path: '/structures/creation',
    title: 'Structures',
    useV6Router: true,
  },
  {
    component: OffererDetails,
    exact: true,
    path: '/structures/:offererId',
    title: 'Structures',
    useV6Router: true,
  },
  {
    component: VenueCreation,
    exact: true,
    path: '/structures/:offererId/lieux/creation',
    title: 'Structures',
    useV6Router: true,
  },
  {
    component: VenueEdition,
    exact: true,
    path: '/structures/:offererId/lieux/:venueId',
    title: 'Structures',
    useV6Router: true,
  },

  {
    component: CollectiveDataEdition,
    exact: true,
    path: '/structures/:offererId/lieux/:venueId/eac',
    title: 'Structures',
    useV6Router: true,
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
    title: 'Offres',
  },
  {
    component: CollectiveOffers,
    exact: true,
    path: '/offres/collectives',
    title: 'Offres',
    useV6Router: true,
  },
  {
    component: CollectiveOfferSelectionDuplication,
    path: '/offre/creation/collectif/selection',
    title: 'Edition d’une offre collective',
    useV6Router: true,
  },
  {
    component: CollectiveOfferStockCreation,
    path: '/offre/:offerId/collectif/stocks',
    title: 'Edition d’une offre collective',
    useV6Router: true,
  },
  {
    component: CollectiveOfferCreation,
    path: '/offre/creation/collectif',
    title: 'Edition d’une offre collective',
    useV6Router: true,
  },
  {
    component: CollectiveOfferCreation,
    path: '/offre/creation/collectif/vitrine',
    title: 'Edition d’une offre collective',
    useV6Router: true,
  },
  {
    component: CollectiveOfferCreation,
    path: '/offre/collectif/:offerId/creation',
    title: 'Edition d’une offre collective',
    useV6Router: true,
  },
  {
    component: CollectiveOfferCreation,
    path: '/offre/collectif/vitrine/:offerId/creation',
    title: 'Edition d’une offre collective',
    useV6Router: true,
  },
  {
    component: CollectiveOfferVisibilityCreation,
    path: '/offre/:offerId/collectif/visibilite',
    title: 'Edition d’une offre collective',
    useV6Router: true,
  },
  {
    component: CollectiveOfferSummaryCreation,
    path: '/offre/:offerId/collectif/creation/recapitulatif',
    title: 'Edition d’une offre collective',
    useV6Router: true,
  },
  {
    component: CollectiveOfferSummaryCreation,
    path: '/offre/:offerId/collectif/vitrine/creation/recapitulatif',
    title: 'Edition d’une offre collective',
    useV6Router: true,
  },
  {
    component: CollectiveOfferConfirmation,
    path: '/offre/:offerId/collectif/confirmation',
    title: 'Edition d’une offre collective',
    useV6Router: true,
  },
  {
    component: CollectiveOfferConfirmation,
    path: '/offre/:offerId/collectif/vitrine/confirmation',
    title: 'Edition d’une offre collective',
    useV6Router: true,
  },
  {
    component: CollectiveOfferEdition,
    path: '/offre/:offerId/collectif/edition',
    title: 'Edition d’une offre collective',
    useV6Router: true,
  },
  {
    component: CollectiveOfferSummaryEdition,
    path: '/offre/:offerId/collectif/recapitulatif',
    title: 'Edition d’une offre collective',
    useV6Router: true,
  },
  {
    component: CollectiveOfferStockEdition,
    path: '/offre/:offerId/collectif/stocks/edition',
    title: 'Edition d’une offre collective',
    useV6Router: true,
  },
  {
    component: CollectiveOfferVisibility,
    path: '/offre/:offerId/collectif/visibilite/edition',
    title: 'Edition d’une offre collective',
    useV6Router: true,
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
    path: '/offre/individuelle/:offerId/*',
    title: 'Offre étape par étape',
    useV6Router: true,
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
    useV6Router: true,
  },
  {
    component: UserProfile,
    path: '/profil',
    useV6Router: true,
    title: 'Profil',
  },
  {
    component: OffererStats,
    path: '/statistiques',
    title: 'Statistiques',
    featureName: 'ENABLE_OFFERER_STATS',
    useV6Router: true,
  },
  {
    component: SignupJourneyRoutes,
    path: '/parcours-inscription/*',
    title: 'Parcours de souscription',
    useV6Router: true,
    featureName: 'WIP_ENABLE_NEW_ONBOARDING',
  },
]

export default routes
