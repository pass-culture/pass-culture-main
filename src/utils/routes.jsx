import React from 'react'
import { Redirect } from 'react-router'

import Accouting from '../components/pages/Accounting'
import BookingsContainer from '../components/pages/Bookings/BookingsContainer'
import DeskContainer from '../components/pages/Desk/DeskContainer'
import Home from '../components/pages/Home'
import Mediation from '../components/pages/Mediation'
import Offers from '../components/pages/Offers'
import Offer from '../components/pages/Offer/OfferContainer'
import OffererContainer from '../components/pages/Offerer/OffererContainer'
import Offerers from '../components/pages/Offerers'
import ProfilContainer from '../components/pages/Profil/ProfilContainer'
import ReimbursementsContainer from '../components/pages/Reimbursements/ReimbursementsContainer'
import Signin from '../components/pages/Signin/Signin'
import Signup from '../components/pages/Signup'
import Terms from '../components/pages/Terms'
import VenueContainer from '../components/pages/Venue/VenueContainer'
import LostPassword from '../components/pages/LostPassword'
import SignupValidationContainer from '../components/pages/Signup/validation/SignupValidationContainer'

// NOTE: routes are sorted by PATH alphabetical order
const routes = [
  {
    path: '/',
    render: () => <Redirect to="/connexion" />,
  },
  {
    component: Home,
    path: '/accueil',
    title: 'Accueil',
  },
  {
    component: Accouting,
    path: '/comptabilite',
    title: 'Comptabilité',
  },
  {
    component: Signin,
    path: '/connexion',
    title: 'Connexion',
  },
  {
    component: DeskContainer,
    path: '/guichet',
    title: 'Guichet',
  },
  {
    component: Signup,
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
    component: LostPassword,
    path: '/mot-de-passe-perdu',
    title: 'Mot de passe perdu',
  },
  {
    component: Offerers,
    path: '/structures',
    title: 'Structures',
  },
  {
    component: OffererContainer,
    path: '/structures/:offererId',
    title: 'Structure',
  },
  {
    component: VenueContainer,
    path: '/structures/:offererId/lieux/:venueId',
    title: 'Lieu',
  },
  {
    component: VenueContainer,
    path: '/structures/:offererId/lieux/:venueId/fournisseurs/:venueProviderId',
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
    component: BookingsContainer,
    path: '/reservations',
    title: 'Réservations',
  },
  {
    component: Offers,
    path: '/offres',
    title: 'Offres',
  },
  {
    component: Offer,
    path: '/offres/:offerId',
    title: 'Offre',
  },
  {
    component: Mediation,
    path: '/offres/:offerId/accroches/:mediationId',
    title: 'Accroche',
  },
  {
    component: Offer,
    path: '/structures/:offererId/offres/:offerId',
    title: 'Offres',
  },
  {
    component: Offer,
    path: '/structures/:offererId/lieux/:venueId/offres/:offerId',
    title: 'Offres',
  },
  {
    component: ProfilContainer,
    path: '/profil',
    title: 'Profil',
  },
]

export default routes
