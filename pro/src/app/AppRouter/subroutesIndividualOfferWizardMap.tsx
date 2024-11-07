/* No need to test this file */
/* istanbul ignore file */
import type { RouteConfig } from './routesMap'

export const routesIndividualOfferWizard: RouteConfig[] = [
  // details pages
  {
    lazy: () =>
      import(
        'pages/IndividualOffer/IndividualOfferDetailsAndInformations/IndividualOfferDetails/IndividualOfferDetails'
      ),
    path: '/offre/individuelle/creation/details',
    title: 'Détails de l’offre - Créer une offre individuelle',
  },
  {
    lazy: () =>
      import(
        'pages/IndividualOffer/IndividualOfferDetailsAndInformations/IndividualOfferDetails/IndividualOfferDetails'
      ),
    path: '/offre/individuelle/:offerId/creation/details',
    title: 'Détails de l’offre - Créer une offre individuelle',
  },
  {
    lazy: () =>
      import('pages/IndividualOfferWizard/DetailsSummary/DetailsSummary'),
    path: '/offre/individuelle/:offerId/recapitulatif/details',
    title: 'Détails de l’offre - Consulter une offre individuelle',
  },
  {
    lazy: () =>
      import(
        'pages/IndividualOffer/IndividualOfferDetailsAndInformations/IndividualOfferDetails/IndividualOfferDetails'
      ),
    path: '/offre/individuelle/:offerId/edition/details',
    title: 'Détails de l’offre - Modifier une offre individuelle',
  },
  // Useful information pages
  {
    lazy: () =>
      import(
        'pages/IndividualOfferWizard/UsefulInformationsSummary/UsefulInformationsSummary'
      ),
    path: '/offre/individuelle/:offerId/pratiques',
    title: 'Informations pratiques - Consulter une offre individuelle',
  },
  {
    lazy: () =>
      import('pages/IndividualOfferWizard/UsefulInformation/UsefulInformation'),
    path: '/offre/individuelle/:offerId/creation/pratiques',
    title: 'Informations pratiques - Créer une offre individuelle',
  },
  {
    lazy: () =>
      import('pages/IndividualOfferWizard/UsefulInformation/UsefulInformation'),
    path: '/offre/individuelle/:offerId/edition/pratiques',
    title: 'Informations pratiques - Modifier une offre individuelle',
  },
  // Price categories pages
  {
    lazy: () =>
      import('pages/IndividualOfferWizard/PriceCategories/PriceCategories'),
    path: '/offre/individuelle/:offerId/creation/tarifs',
    title: 'Tarifs - Créer une offre individuelle',
  },
  {
    lazy: () =>
      import('pages/IndividualOfferWizard/PriceCategories/PriceCategories'),
    path: '/offre/individuelle/:offerId/edition/tarifs',
    title: 'Tarifs - Modifier une offre individuelle',
  },
  {
    lazy: () =>
      import(
        'pages/IndividualOfferWizard/PriceCategoriesSummary/PriceCategoriesSummary'
      ),
    path: '/offre/individuelle/:offerId/tarifs',
    title: 'Tarifs - Consulter une offre individuelle',
  },
  // Stocks pages
  {
    lazy: () => import('pages/IndividualOfferWizard/Stocks/Stocks'),
    path: '/offre/individuelle/:offerId/creation/stocks',
    title: 'Stocks et prix - Créer une offre individuelle',
  },
  {
    lazy: () => import('pages/IndividualOfferWizard/Stocks/Stocks'),
    path: '/offre/individuelle/:offerId/edition/stocks',
    title: 'Stocks et prix - Modifier une offre individuelle',
  },
  {
    lazy: () =>
      import('pages/IndividualOfferWizard/StocksSummary/StocksSummary'),
    path: '/offre/individuelle/:offerId/stocks',
    title: 'Stocks et prix - Consulter une offre individuelle',
  },
  // Summary pages
  {
    lazy: () => import('pages/IndividualOfferWizard/Summary/Summary'),
    path: '/offre/individuelle/:offerId/creation/recapitulatif',
    title: 'Récapitulatif - Créer une offre individuelle',
  },
  {
    lazy: () => import('pages/IndividualOfferWizard/Summary/Summary'),
    path: '/offre/individuelle/:offerId/recapitulatif',
    title: 'Récapitulatif - Modifier une offre individuelle',
  },
  // confirmation pages
  {
    lazy: () =>
      import(
        'pages/IndividualOffer/IndividualOfferConfirmation/IndividualOfferConfirmation'
      ),
    path: '/offre/individuelle/:offerId/creation/confirmation',
    title: 'Confirmation - Offre individuelle publiée',
  },
  {
    lazy: () =>
      import(
        'pages/IndividualOffer/IndividualOfferConfirmation/IndividualOfferConfirmation'
      ),
    path: '/offre/individuelle/:offerId/confirmation',
    title: 'Confirmation - Offre individuelle publiée',
  },
  // booking summary page
  {
    lazy: () =>
      import(
        'pages/IndividualOffer/IndividualOfferSummary/IndividualOfferBookings/IndividualOfferBookings'
      ),
    path: '/offre/individuelle/:offerId/reservations',
    title: 'Réservations - Consulter une offre individuelle',
  },
]
