/* No need to test this file */
/* istanbul ignore file */
import React from 'react'

import { Confirmation } from 'pages/OfferIndividualWizard/Confirmation'
import { Offer } from 'pages/OfferIndividualWizard/Offer'
import { PriceCategories } from 'pages/OfferIndividualWizard/PriceCategories'
import { Stocks } from 'pages/OfferIndividualWizard/Stocks'
import { Summary } from 'pages/OfferIndividualWizard/Summary'

import type { IRoute } from './routesMap'

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

export default routesOfferIndividualWizard
