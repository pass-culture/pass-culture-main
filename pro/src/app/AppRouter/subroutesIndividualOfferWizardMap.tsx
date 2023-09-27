/* No need to test this file */
/* istanbul ignore file */

import React from 'react'

import { Confirmation } from 'pages/IndividualOfferWizard/Confirmation'
import { Offer } from 'pages/IndividualOfferWizard/Offer'
import { PriceCategories } from 'pages/IndividualOfferWizard/PriceCategories/PriceCategories'
import { PriceCategoriesSummary } from 'pages/IndividualOfferWizard/PriceCategoriesSummary/PriceCategoriesSummary'
import { Stocks } from 'pages/IndividualOfferWizard/Stocks'
import { StocksSummary } from 'pages/IndividualOfferWizard/StocksSummary/StocksSummary'
import { Summary } from 'pages/IndividualOfferWizard/Summary/Summary'

import type { RouteConfig } from './routesMap'

export const routesIndividualOfferWizard: RouteConfig[] = [
  {
    element: <Offer />,
    parentPath: '/offre/individuelle/:offerId',
    path: '/informations',
    title: 'Détails - Consulter une offre individuelle',
  },
  {
    element: <Offer />,
    // This route is duplicated with the one above because
    // /offre/individuelle/creation also matches /offre/individuelle/:offerId
    // but we do not want to display the same title for both routes
    // In addition, this route is placed after the one above because
    // in usePageTitle we `.reverse()` the routes list when matching paths
    // to find the title. So this one is after so that `creation` is matched first
    // when displaying the title.
    // Ultimately, the best solution would be to have different urls that don't overlap
    // but this would require a lot of refactoring/changes
    parentPath: '/offre/individuelle/creation',
    path: '/informations',
    title: 'Création - Détail de l’offre',
  },
  {
    element: <Offer />,
    parentPath: '/offre/individuelle/:offerId',
    path: '/creation/informations',
    title: 'Détails - Créer une offre individuelle',
  },
  {
    element: <Offer />,
    parentPath: '/offre/individuelle/:offerId',
    path: '/brouillon/informations',
    title: 'Détails - Brouillon d’une offre individuelle',
  },
  {
    element: <Offer />,
    parentPath: '/offre/individuelle/:offerId',
    path: '/edition/informations',
    title: 'Détails - Modifier une offre individuelle',
  },
  {
    element: <PriceCategories />,
    parentPath: '/offre/individuelle/:offerId',
    path: '/creation/tarifs',
    title: 'Tarifs - Créer une offre individuelle',
  },
  {
    element: <PriceCategories />,
    parentPath: '/offre/individuelle/:offerId',
    path: '/brouillon/tarifs',
    title: 'Tarifs - Brouillon d’une offre individuelle',
  },
  {
    element: <PriceCategories />,
    parentPath: '/offre/individuelle/:offerId',
    path: '/edition/tarifs',
    title: 'Tarifs - Modifier une offre individuelle',
  },
  {
    element: <PriceCategoriesSummary />,
    parentPath: '/offre/individuelle/:offerId',
    path: '/tarifs',
    title: 'Tarifs - Consulter une offre individuelle',
  },
  {
    element: <Stocks />,
    parentPath: '/offre/individuelle/:offerId',
    path: '/creation/stocks',
    title: 'Stocks et prix  - Créer une offre individuelle',
  },
  {
    element: <Stocks />,
    parentPath: '/offre/individuelle/:offerId',
    path: '/brouillon/stocks',
    title: 'Stocks et prix - Brouillon d’une offre individuelle',
  },
  {
    element: <Stocks />,
    parentPath: '/offre/individuelle/:offerId',
    path: '/edition/stocks',
    title: 'Stocks et prix  - Modifier une offre individuelle',
  },
  {
    element: <StocksSummary />,
    parentPath: '/offre/individuelle/:offerId',
    path: '/stocks',
    title: 'Stocks et prix  - Consulter une offre individuelle',
  },
  {
    element: <Summary />,
    parentPath: '/offre/individuelle/:offerId',
    path: '/creation/recapitulatif',
    title: 'Récapitulatif  - Créer une offre individuelle',
  },
  {
    element: <Summary />,
    parentPath: '/offre/individuelle/:offerId',
    path: '/brouillon/recapitulatif',
    title: 'Récapitulatif - Brouillon d’une offre individuelle',
  },
  {
    element: <Summary />,
    parentPath: '/offre/individuelle/:offerId',
    path: '/recapitulatif',
    title: 'Récapitulatif - Modifier une offre individuelle',
  },
  {
    element: <Confirmation />,
    parentPath: '/offre/individuelle/:offerId',
    path: '/creation/confirmation',
    title: 'Confirmation - Offre individuelle publiée',
  },
  {
    element: <Confirmation />,
    parentPath: '/offre/individuelle/:offerId',
    path: '/brouillon/confirmation',
    title: 'Confirmation - Brouillon d’une offre individuelle publié',
  },
  {
    element: <Confirmation />,
    parentPath: '/offre/individuelle/:offerId',
    path: '/confirmation',
    title: 'Confirmation - Offre individuelle publiée',
  },
]

export default routesIndividualOfferWizard
