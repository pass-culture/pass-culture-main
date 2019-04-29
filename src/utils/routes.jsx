import React from 'react'
import { Redirect } from 'react-router'

import Accouting from '../components/pages/Accounting'
import Desk from '../components/pages/Desk'
import Home from '../components/pages/Home'
import Mediation from '../components/pages/Mediation'
import MonitoringContainer from '../components/pages/Monitoring/MonitoringContainer'
import Offers from '../components/pages/Offers'
import Offer from '../components/pages/Offer'
import OffererContainer from '../components/pages/Offerer/OffererContainer'
import Offerers from '../components/pages/Offerers'
import Profile from '../components/pages/Profile'
import Signin from '../components/pages/Signin'
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
    component: Desk,
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
    component: MonitoringContainer,
    path: '/suivi/:view(reservations|remboursements)?',
    title: 'Suivi',
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
    component: Profile,
    path: '/profil',
    title: 'Profil',
  },
]

export default routes
