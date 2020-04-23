import React from 'react'
import { Redirect } from 'react-router'
import CsvDetailViewContainer from '../components/layout/CsvTable/CsvTableContainer'
import DeskContainer from '../components/pages/Desk/DeskContainer'
import HomeContainer from '../components/pages/Home/HomeContainer'
import LostPasswordContainer from '../components/pages/LostPassword/LostPasswordContainer'
import Mediation from '../components/pages/Mediation/MediationContainer'
import Offers from '../components/pages/Offers/OffersContainer'
import OfferCreation from '../components/pages/Offer/OfferCreation/OfferCreationContainer'
import OfferEdition from '../components/pages/Offer/OfferEdition/OfferEditionContainer'
import Offerers from '../components/pages/Offerers/OfferersContainer'
import ProfilContainer from '../components/pages/Profil/ProfilContainer'
import ReimbursementsContainer from '../components/pages/Reimbursements/ReimbursementsContainer'
import SigninContainer from '../components/pages/Signin/SigninContainer'
import SignupContainer from '../components/pages/Signup/SignupContainer'
import SignupValidationContainer from '../components/pages/Signup/SignupValidation/SignupValidationContainer'
import Terms from '../components/pages/Terms/Terms'
import VenueCreationContainer from '../components/pages/Venue/VenueCreation/VenueCreationContainer'
import VenueEditionContainer from '../components/pages/Venue/VenueEdition/VenueEditionContainer'
import OffererCreationContainer from '../components/pages/Offerer/OffererCreation/OffererCreationContainer'
import OffererDetailsContainer from '../components/pages/Offerer/OffererDetails/OffererDetailsContainer'
import BookingsRouterContainer from '../components/hocs/bookings-router/BookingsRouterContainer'

const RedirectToConnexionComponent = () => <Redirect to="/connexion" />

// NOTE: routes are sorted by PATH alphabetical order
const routes = [
  {
    component: RedirectToConnexionComponent,
    path: '/',
  },
  {
    component: HomeContainer,
    path: '/accueil',
    title: 'Accueil',
  },
  {
    component: SigninContainer,
    path: '/connexion',
    title: 'Connexion',
  },
  {
    component: DeskContainer,
    path: '/guichet',
    title: 'Guichet',
  },
  {
    component: SignupContainer,
    path: '/inscription/(confirmation)?',
    title: 'Inscription',
  },
  {
    component: SignupValidationContainer,
    path: '/inscription/validation/:token',
    title: 'Validation de votre inscription',
  },
  {
    component: Terms,
    path: '/mentions-legales',
    title: 'Mentions Légales',
  },
  {
    component: LostPasswordContainer,
    path: '/mot-de-passe-perdu',
    title: 'Mot de passe perdu',
  },
  {
    component: Offerers,
    path: '/structures',
    title: 'Structures',
  },
  {
    component: OffererCreationContainer,
    path: '/structures/creation',
    title: 'Structure',
  },
  {
    component: OffererDetailsContainer,
    path: '/structures/:offererId',
    title: 'Structure',
  },
  {
    component: VenueCreationContainer,
    path: '/structures/:offererId/lieux/creation',
    title: 'Lieu',
  },
  {
    component: VenueEditionContainer,
    path: '/structures/:offererId/lieux/:venueId/modification',
    title: 'Lieu',
  },
  {
    component: VenueEditionContainer,
    path: '/structures/:offererId/lieux/:venueId',
    title: 'Lieu',
  },
  {
    component: Offers,
    path: '/structures/:offererId/lieux/:venueId/offres',
    title: 'Offres',
  },
  {
    component: ReimbursementsContainer,
    path: '/remboursements',
    title: 'Remboursements',
  },
  {
    component: BookingsRouterContainer,
    featureName: 'BOOKINGS_V2',
    path: '/reservations',
    title: 'Réservations',
  },
  {
    component: Offers,
    path: '/offres',
    title: 'Offres',
  },
  {
    component: OfferCreation,
    path: '/offres/:offerId',
    title: 'Offre',
  },
  {
    component: OfferEdition,
    path: '/offres/:offerId/edition',
    title: "Edition d'une offre",
  },
  {
    component: Mediation,
    path: '/offres/:offerId/accroches/:mediationId',
    title: 'Accroche',
  },
  {
    component: OfferCreation,
    path: '/structures/:offererId/offres/:offerId',
    title: 'Offres',
  },
  {
    component: OfferCreation,
    path: '/structures/:offererId/lieux/:venueId/offres/:offerId',
    title: 'Offres',
  },
  {
    component: ProfilContainer,
    path: '/profil',
    title: 'Profil',
  },
  {
    component: CsvDetailViewContainer,
    path: '/reservations/detail',
    title: 'Réservations',
  },
  {
    component: CsvDetailViewContainer,
    path: '/remboursements/detail',
    title: 'Remboursements',
  },
]

export default routes
