import { Redirect, useLocation } from 'react-router-dom'

import Unavailable from 'components/pages/Errors/Unavailable/Unavailable'
import Homepage from 'components/pages/Home/Homepage'
import LostPassword from 'components/pages/LostPassword/LostPassword'
import Offerers from 'components/pages/Offerers/List/Offerers'
import OffererDetails from 'components/pages/Offerers/Offerer/OffererDetails/OffererDetails'
import VenueV1Creation from 'components/pages/Offerers/Offerer/VenueV1/VenueCreation/VenueCreation'
import CollectiveDataEdition from 'components/pages/Offerers/Offerer/VenueV1/VenueEdition/CollectiveDataEdition'
import VenueV1Edition from 'components/pages/Offerers/Offerer/VenueV1/VenueEdition/VenueEdition'
import OffererCreation from 'components/pages/Offerers/OffererCreation'
import OfferLayout from 'components/pages/Offers/Offer/OfferLayout'
import Reimbursements from 'components/pages/Reimbursements'
import SetPassword from 'components/pages/SetPassword/SetPassword'
import SetPasswordConfirm from 'components/pages/SetPasswordConfirm/SetPasswordConfirm'
import SignIn from 'components/pages/SignIn/SignIn'
import Signup from 'components/pages/Signup/Signup'
import Bookings from 'routes/Bookings'
import BusinessUnitList from 'routes/BusinessUnitList'
import CollectiveBookings from 'routes/CollectiveBookings'
import CollectiveOfferConfirmation from 'routes/CollectiveOfferConfirmation'
import CollectiveOffers from 'routes/CollectiveOffers'
import CollectiveOfferCreationVisibility from 'routes/CollectiveOfferVisibility/CollectiveOfferCreationVisibility'
import CsvTable from 'routes/CsvTable'
import Desk from 'routes/Desk'
import { EmailChangeValidation } from 'routes/EmailChangeValidation'
import OfferEducationalCreation from 'routes/OfferEducationalCreation'
import OfferEducationalStockCreation from 'routes/OfferEducationalStockCreation'
import { OfferIndividualWizard } from 'routes/OfferIndividualWizard'
import Offers from 'routes/Offers'
import OfferType from 'routes/OfferType'
import SignUpValidation from 'routes/SignUpValidation'
import { UserProfile } from 'routes/User'
import { VenueCreation } from 'routes/VenueCreation'
import { VenueEdition } from 'routes/VenueEdition'
import { UNAVAILABLE_ERROR_PAGE } from 'utils/routes'

import CollectiveOfferCreationFromTemplate from './CollectiveOfferCreationFromTemplate'
import CollectiveOfferEditionRoutes from './CollectiveOfferEditionRoutes'
import CollectiveOfferStockCreationFromTemplate from './CollectiveOfferStockCreationFromTemplate'
import CollectiveOfferTemplateEditionRoutes from './CollectiveOfferTemplateEditionRoutes'
import { OffererStats } from './OffererStats'

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
  },
  {
    component: VenueV1Edition,
    exact: true,
    path: '/structures/:offererId([A-Z0-9]+)/lieux/:venueId([A-Z0-9]+)',
    title: 'Structures',
  },
  {
    component: VenueCreation,
    exact: true,
    path: '/structures/:offererId([A-Z0-9]+)/lieux/v2/creation',
    title: 'Structures',
    featureName: 'VENUE_FORM_V2',
  },
  {
    component: VenueEdition,
    exact: true,
    path: '/structures/:offererId([A-Z0-9]+)/lieux/v2/:venueId([A-Z0-9]+)',
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
    component: OfferEducationalCreation,
    exact: true,
    path: '/offre/creation/collectif',
    title: 'Offre collective',
  },
  {
    component: CollectiveOfferCreationFromTemplate,
    exact: true,
    path: '/offre/duplication/collectif/:templateId([A-Z0-9]+)',
    title: 'Offre collective',
    featureName: 'WIP_CREATE_COLLECTIVE_OFFER_FROM_TEMPLATE',
  },
  {
    component: Offers,
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
    component: OfferEducationalStockCreation,
    exact: true,
    path: '/offre/:offerId([A-Z0-9]+)/collectif/stocks',
    title: 'Stock lié à une offre collective',
  },
  {
    component: CollectiveOfferStockCreationFromTemplate,
    exact: true,
    path: '/offre/duplication/collectif/:offerId([A-Z0-9]+)/stock',
    title: 'Stock lié à une offre collective',
    featureName: 'WIP_CREATE_COLLECTIVE_OFFER_FROM_TEMPLATE',
  },
  {
    component: CollectiveOfferCreationVisibility,
    exact: true,
    path: '/offre/:offerId([A-Z0-9]+)/collectif/visibilite',
    title: 'Visibilité d’une offre collective',
  },
  {
    component: CollectiveOfferConfirmation,
    exact: true,
    path: '/offre/:offerId/collectif/confirmation',
    title: 'Page de confirmation de création d’offre',
  },
  {
    component: CollectiveOfferEditionRoutes,
    exact: false,
    path: '/offre/:offerId([A-Z0-9]+)/collectif',
    title: 'Edition d’une offre collective',
  },
  {
    component: CollectiveOfferTemplateEditionRoutes,
    exact: false,
    path: '/offre/:offerId(T-[A-Z0-9]+)/collectif',
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
