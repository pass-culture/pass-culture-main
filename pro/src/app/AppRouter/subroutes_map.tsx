/* No need to test this file */
/* istanbul ignore file */
import React from 'react'

import { Confirmation } from 'pages/OfferIndividualWizard/Confirmation'
import { Offer } from 'pages/OfferIndividualWizard/Offer'
import { PriceCategories } from 'pages/OfferIndividualWizard/PriceCategories'
import { Stocks } from 'pages/OfferIndividualWizard/Stocks'
import { Summary } from 'pages/OfferIndividualWizard/Summary'
import SignupConfirmation from 'pages/Signup/SignupConfirmation/SignupConfirmation'
import SignupContainer from 'pages/Signup/SignupContainer/SignupContainer'
import SignUpValidation from 'pages/Signup/SignUpValidation'
import { Activity } from 'screens/SignupJourneyForm/Activity'
import { OffererAuthentication } from 'screens/SignupJourneyForm/Authentication'
import { ConfirmedAttachment } from 'screens/SignupJourneyForm/ConfirmedAttachment'
import { Offerer } from 'screens/SignupJourneyForm/Offerer'
import { Offerers as SignupJourneyOfferers } from 'screens/SignupJourneyForm/Offerers'
import { Validation } from 'screens/SignupJourneyForm/Validation'
import { Welcome } from 'screens/SignupJourneyForm/Welcome'

import type { IRoute, RouteDefinition } from './routes_map'

export const routesOfferIndividualWizard: IRoute[] = [
  {
    element: <Offer />,
    parentPath: '/offre/individuelle/:offerId',
    path: '/informations',
    title: 'Détails de l’offre',
  },
  {
    element: <Offer />,
    parentPath: '/offre/individuelle/:offerId',
    path: '/creation/informations',
    title: 'Détails de l’offre',
  },
  {
    element: <Offer />,
    parentPath: '/offre/individuelle/:offerId',
    path: '/brouillon/informations',
    title: 'Détails de l’offre',
  },
  {
    element: <PriceCategories />,
    parentPath: '/offre/individuelle/:offerId',
    path: '/creation/tarifs',
    title: 'Vos tarifs',
  },
  {
    element: <PriceCategories />,
    parentPath: '/offre/individuelle/:offerId',
    path: '/brouillon/tarifs',
    title: 'Vos tarifs',
  },
  {
    element: <PriceCategories />,
    parentPath: '/offre/individuelle/:offerId',
    path: '/tarifs',
    title: 'Vos tarifs',
  },
  {
    element: <Stocks />,
    parentPath: '/offre/individuelle/:offerId',
    path: '/creation/stocks',
    title: 'Vos stocks',
  },
  {
    element: <Stocks />,
    parentPath: '/offre/individuelle/:offerId',
    path: '/brouillon/stocks',
    title: 'Vos stocks',
  },
  {
    element: <Stocks />,
    parentPath: '/offre/individuelle/:offerId',
    path: '/stocks',
    title: 'Vos stocks',
  },
  {
    element: <Summary />,
    parentPath: '/offre/individuelle/:offerId',
    path: '/creation/recapitulatif',
    title: 'Récapitulatif',
  },
  {
    element: <Summary />,
    parentPath: '/offre/individuelle/:offerId',
    path: '/brouillon/recapitulatif',
    title: 'Récapitulatif',
  },
  {
    element: <Summary />,
    parentPath: '/offre/individuelle/:offerId',
    path: '/recapitulatif',
    title: 'Récapitulatif',
  },
  {
    element: <Confirmation />,
    parentPath: '/offre/individuelle/:offerId',
    path: '/creation/confirmation',
    title: 'Confirmation',
  },
  {
    element: <Confirmation />,
    parentPath: '/offre/individuelle/:offerId',
    path: '/brouillon/confirmation',
    title: 'Confirmation',
  },
  {
    element: <Confirmation />,
    parentPath: '/offre/individuelle/:offerId',
    path: '/confirmation',
    title: 'Confirmation',
  },
]

export const routesSignup: IRoute[] = [
  {
    element: <SignupContainer />,
    parentPath: '/inscription',
    path: '/',
    title: 'S’inscrire',
  },
  {
    element: <SignupConfirmation />,
    parentPath: '/inscription',
    path: '/confirmation',
    title: 'S’inscrire',
  },
  {
    element: <SignUpValidation />,
    parentPath: '/inscription',
    path: '/validation/:token',
    title: 'S’inscrire',
  },
]

export const routesSignupJourney: IRoute[] = [
  {
    element: <Welcome />,
    parentPath: '/parcours-inscription',
    path: '/',
    title: '',
  },
  {
    element: <Offerer />,
    parentPath: '/parcours-inscription',
    path: '/structure',
    title: '',
  },
  {
    element: <SignupJourneyOfferers />,
    parentPath: '/parcours-inscription',
    path: '/structure/rattachement',
    title: '',
  },
  {
    element: <ConfirmedAttachment />,
    parentPath: '/parcours-inscription',
    path: '/structure/rattachement/confirmation',
    title: '',
  },
  {
    element: <OffererAuthentication />,
    parentPath: '/parcours-inscription',
    path: '/authentification',
    title: '',
  },
  {
    element: <OffererAuthentication />,
    parentPath: '/parcours-inscription',
    path: '/authentification',
    title: '',
  },
  {
    element: <Activity />,
    parentPath: '/parcours-inscription',
    path: '/activite',
    title: '',
  },
  {
    element: <Validation />,
    parentPath: '/parcours-inscription',
    path: '/validation',
    title: '',
  },
]

export const subroutesDefinitions: RouteDefinition[] = [
  ...routesOfferIndividualWizard,
  ...routesSignup,
  ...routesSignupJourney,
].map(({ path, parentPath, title }) => {
  return { path, parentPath, title }
})
