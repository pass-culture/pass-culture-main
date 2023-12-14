/* No need to test this file */
/* istanbul ignore file */
import React from 'react'
import { Navigate } from 'react-router-dom'

import { BookingsSummary } from 'pages/IndividualOfferWizard/BookingsSummary/BookingsSummary'
import Confirmation from 'pages/IndividualOfferWizard/Confirmation/Confirmation'
import Offer from 'pages/IndividualOfferWizard/Offer/Offer'
import { PriceCategories } from 'pages/IndividualOfferWizard/PriceCategories/PriceCategories'
import { PriceCategoriesSummary } from 'pages/IndividualOfferWizard/PriceCategoriesSummary/PriceCategoriesSummary'
import Stocks from 'pages/IndividualOfferWizard/Stocks/Stocks'
import { StocksSummary } from 'pages/IndividualOfferWizard/StocksSummary/StocksSummary'
import { Summary } from 'pages/IndividualOfferWizard/Summary/Summary'

import type { RouteConfig } from './routesMap'

export const routesIndividualOfferWizard: RouteConfig[] = [
  {
    element: <Offer />,
    path: '/offre/individuelle/:offerId/informations',
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
    path: '/offre/individuelle/:offerId/informations',
    title: 'Création - Détail de l’offre',
  },
  {
    element: <Offer />,
    path: '/offre/individuelle/:offerId/creation/informations',
    title: 'Détails - Créer une offre individuelle',
  },
  {
    element: <Offer />,
    path: '/offre/individuelle/:offerId/edition/informations',
    title: 'Détails - Modifier une offre individuelle',
  },
  {
    element: <PriceCategories />,
    path: '/offre/individuelle/:offerId/creation/tarifs',
    title: 'Tarifs - Créer une offre individuelle',
  },
  {
    element: <PriceCategories />,
    path: '/offre/individuelle/:offerId/edition/tarifs',
    title: 'Tarifs - Modifier une offre individuelle',
  },
  {
    element: <PriceCategoriesSummary />,
    path: '/offre/individuelle/:offerId/tarifs',
    title: 'Tarifs - Consulter une offre individuelle',
  },
  {
    element: <Stocks />,
    path: '/offre/individuelle/:offerId/creation/stocks',
    title: 'Stocks et prix - Créer une offre individuelle',
  },
  {
    element: <Stocks />,
    path: '/offre/individuelle/:offerId/edition/stocks',
    title: 'Stocks et prix - Modifier une offre individuelle',
  },
  {
    element: <StocksSummary />,
    path: '/offre/individuelle/:offerId/stocks',
    title: 'Stocks et prix - Consulter une offre individuelle',
  },
  {
    element: <Summary />,
    path: '/offre/individuelle/:offerId/creation/recapitulatif',
    title: 'Récapitulatif - Créer une offre individuelle',
  },
  {
    element: <Summary />,
    path: '/offre/individuelle/:offerId/recapitulatif',
    title: 'Récapitulatif - Modifier une offre individuelle',
  },
  {
    element: <Confirmation />,
    path: '/offre/individuelle/:offerId/creation/confirmation',
    title: 'Confirmation - Offre individuelle publiée',
  },
  {
    element: <Confirmation />,
    path: '/offre/individuelle/:offerId/confirmation',
    title: 'Confirmation - Offre individuelle publiée',
  },
  {
    element: <BookingsSummary />,
    path: '/offre/individuelle/:offerId/reservations',
    title: 'Réservations - Consulter une offre individuelle',
  },
  // Deprecated routes, should be deleted in 6 months (09/04/2024)
  {
    element: <Navigate to="../creation/informations" replace={true} />,
    path: '/offre/individuelle/:offerId/brouillon/informations',
    title: 'Détails - Brouillon d’une offre individuelle',
  },
  {
    element: <Navigate to="../creation/tarifs" replace={true} />,
    path: '/offre/individuelle/:offerId/brouillon/tarifs',
    title: 'Tarifs - Brouillon d’une offre individuelle',
  },
  {
    element: <Navigate to="../creation/stocks" replace={true} />,
    path: '/offre/individuelle/:offerId/brouillon/stocks',
    title: 'Stocks et prix - Brouillon d’une offre individuelle',
  },
  {
    element: <Navigate to="../creation/confirmation" replace={true} />,
    path: '/offre/individuelle/:offerId/brouillon/confirmation',
    title: 'Confirmation - Brouillon d’une offre individuelle publié',
  },
  {
    element: <Navigate to="../creation/recapitulatif" replace={true} />,
    path: '/offre/individuelle/:offerId/brouillon/recapitulatif',
    title: 'Récapitulatif - Brouillon d’une offre individuelle',
  },
]
