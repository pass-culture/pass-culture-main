import { Redirect, useLocation } from 'react-router-dom'

import Unavailable from 'components/pages/Errors/Unavailable/Unavailable'
import Homepage from 'components/pages/Home/Homepage'
import LostPassword from 'components/pages/LostPassword/LostPassword'
import OfferersContainer from 'components/pages/Offerers/List/OfferersContainer'
import OffererDetails from 'components/pages/Offerers/Offerer/OffererDetails/OffererDetails'
import VenueCreation from 'components/pages/Offerers/Offerer/VenueV1/VenueCreation/VenueCreation'
import CollectiveDataEdition from 'components/pages/Offerers/Offerer/VenueV1/VenueEdition/CollectiveDataEdition'
import VenueEdition from 'components/pages/Offerers/Offerer/VenueV1/VenueEdition/VenueEdition'
import OffererCreation from 'components/pages/Offerers/OffererCreation'
import OfferLayout from 'components/pages/Offers/Offer/OfferLayout'
import { Reimbursements } from 'components/pages/Reimbursements'
import SetPasswordContainer from 'components/pages/SetPassword/SetPasswordContainer'
import SetPasswordConfirmContainer from 'components/pages/SetPasswordConfirm/SetPasswordConfirmContainer'
import SignIn from 'components/pages/SignIn/SignIn'
import Signup from 'components/pages/Signup/Signup'
import Bookings from 'routes/Bookings'
import BusinessUnitList from 'routes/BusinessUnitList'
import CollectiveBookings from 'routes/CollectiveBookings'
import CollectiveOfferConfirmation from 'routes/CollectiveOfferConfirmation'
import CollectiveOffers from 'routes/CollectiveOffers'
import CollectiveOfferTemplateStockEdition from 'routes/CollectiveOfferTemplateStockEdition'
import CollectiveOfferCreationVisibility from 'routes/CollectiveOfferVisibility/CollectiveOfferCreationVisibility'
import CollectiveOfferEditionVisibility from 'routes/CollectiveOfferVisibility/CollectiveOfferEditionVisibility'
import CsvDetailViewContainer from 'routes/CsvTable'
import Desk from 'routes/Desk'
import OfferEducationalCreation from 'routes/OfferEducationalCreation'
import OfferEducationalEdition from 'routes/OfferEducationalEdition'
import OfferEducationalStockCreation from 'routes/OfferEducationalStockCreation'
import OfferEducationalStockEdition from 'routes/OfferEducationalStockEdition/OfferEducationalStockEdition'
import { OfferIndividualConfirmation } from 'routes/OfferIndividualConfirmation'
import { OfferIndividualCreation } from 'routes/OfferIndividualCreation'
import Offers from 'routes/Offers'
import OfferType from 'routes/OfferType'
import SignUpValidation from 'routes/SignUpValidation'
import { UserProfile } from 'routes/User'
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
    component: CsvDetailViewContainer,
    exact: true,
    path: '/reservations/detail',
    title: 'Réservations',
  },
  {
    component: CsvDetailViewContainer,
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
    component: SetPasswordContainer,
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
    component: SetPasswordConfirmContainer,
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
    component: OfferersContainer,
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
    component: CollectiveOfferCreationVisibility,
    exact: true,
    path: '/offre/:offerId([A-Z0-9]+)/collectif/visibilite',
    title: 'Visibilité d’une offre collective',
  },
  {
    component: CollectiveOfferConfirmation,
    exact: true,
    path: '/offre/:offerId([A-Z0-9]+)/collectif/confirmation',
    title: 'Page de confirmation de création d’offre',
  },
  {
    component: CollectiveOfferConfirmation,
    exact: true,
    path: '/offre/:offerId(T-[A-Z0-9]+)/collectif/confirmation',
    title: 'Page de confirmation de création d’offre',
  },
  {
    component: OfferEducationalEdition,
    exact: true,
    path: '/offre/:offerId([A-Z0-9]+)/collectif/edition',
    title: 'Edition d’une offre collective',
  },
  {
    component: OfferEducationalEdition,
    exact: true,
    path: '/offre/:offerId(T-[A-Z0-9]+)/collectif/edition',
    title: 'Edition d’une offre collective',
  },
  {
    component: OfferEducationalStockEdition,
    exact: true,
    path: '/offre/:offerId([A-Z0-9]+)/collectif/stocks/edition',
    title: 'Edition d’un stock d’une offre collective',
  },
  {
    component: CollectiveOfferTemplateStockEdition,
    exact: true,
    path: '/offre/:offerId(T-[A-Z0-9]+)/collectif/stocks/edition',
    title: 'Edition d’un stock d’une offre collective',
  },
  {
    component: CollectiveOfferEditionVisibility,
    exact: true,
    path: '/offre/:offerId([A-Z0-9]+)/collectif/visibilite/edition',
    title: 'Edition de la visibilité d’une offre collective',
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
    component: OfferIndividualConfirmation,
    exact: true,
    path: '/offre/:offerId/v3/creation/individuelle/confirmation',
    title: "Confirmation de création d'offre",
    featureName: 'OFFER_FORM_V3',
  },
  {
    component: OfferIndividualCreation,
    exact: false,
    path: [
      '/offre/v3/creation/individuelle',
      '/offre/:offerId/v3/creation/individuelle',
    ],
    title: 'Résumé de votre offre',
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
    path: '/profile',
    title: 'Profil',
    featureName: 'ENABLE_IN_PAGE_PROFILE_FORM',
  },
]

export default routes
