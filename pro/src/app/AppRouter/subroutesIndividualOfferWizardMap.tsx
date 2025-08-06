/* No need to test this file */
/* istanbul ignore file */
import type { RouteConfig } from './routesMap'

export const routesIndividualOfferWizard: RouteConfig[] = [
  // Details pages
  {
    lazy: () =>
      import(
        '@/pages/IndividualOffer/IndividualOfferDetails/IndividualOfferDetails'
      ),
    path: '/offre/individuelle/creation/details',
    title: 'Détails de l’offre - Créer une offre individuelle',
  },
  {
    lazy: () =>
      import(
        '@/pages/IndividualOffer/IndividualOfferDetails/IndividualOfferDetails'
      ),
    path: '/offre/individuelle/:offerId/creation/details',
    title: 'Détails de l’offre - Créer une offre individuelle',
  },
  {
    lazy: () =>
      import(
        '@/pages/IndividualOffer/IndividualOfferDetails/IndividualOfferDetails'
      ),
    path: '/offre/individuelle/:offerId/edition/details',
    title: 'Détails de l’offre - Modifier une offre individuelle',
  },
  {
    lazy: () =>
      import(
        '@/pages/IndividualOfferSummary/IndividualOfferSummaryDetails/IndividualOfferSummaryDetails'
      ),
    path: '/offre/individuelle/:offerId/recapitulatif/details',
    title: 'Détails de l’offre - Consulter une offre individuelle',
  },
  // Information pages
  {
    lazy: () =>
      import(
        '@/pages/IndividualOffer/IndividualOfferInformations/IndividualOfferInformations'
      ),
    path: '/offre/individuelle/:offerId/creation/pratiques',
    title: 'Informations pratiques - Créer une offre individuelle',
  },
  {
    lazy: () =>
      import(
        '@/pages/IndividualOffer/IndividualOfferInformations/IndividualOfferInformations'
      ),
    path: '/offre/individuelle/:offerId/edition/pratiques',
    title: 'Informations pratiques - Modifier une offre individuelle',
  },
  {
    lazy: () =>
      import(
        '@/pages/IndividualOfferSummary/IndividualOfferSummaryInformations/IndividualOfferSummaryInformations'
      ),
    path: '/offre/individuelle/:offerId/pratiques',
    title: 'Informations pratiques - Consulter une offre individuelle',
  },
  // Image & video (media) pages
  {
    lazy: () =>
      import(
        '@/pages/IndividualOffer/IndividualOfferMedia/IndividualOfferMedia'
      ),
    path: '/offre/individuelle/:offerId/creation/media',
    title: 'Image et vidéo - Créer une offre individuelle',
  },
  {
    lazy: () =>
      import(
        '@/pages/IndividualOffer/IndividualOfferMedia/IndividualOfferMedia'
      ),
    path: '/offre/individuelle/:offerId/edition/media',
    title: 'Image et vidéo - Modifier une offre individuelle',
  },
  {
    lazy: () =>
      import(
        '@/pages/IndividualOfferSummary/IndividualOfferSummaryMedia/IndividualOfferSummaryMedia'
      ),
    path: '/offre/individuelle/:offerId/media',
    title: 'Image et vidéo - Consulter une offre individuelle',
  },
  // Price categories pages
  {
    lazy: () =>
      import('@/pages/IndividualOfferWizard/PriceCategories/PriceCategories'),
    path: '/offre/individuelle/:offerId/creation/tarifs',
    title: 'Tarifs - Créer une offre individuelle',
  },
  {
    lazy: () =>
      import('@/pages/IndividualOfferWizard/PriceCategories/PriceCategories'),
    path: '/offre/individuelle/:offerId/edition/tarifs',
    title: 'Tarifs - Modifier une offre individuelle',
  },
  {
    lazy: () =>
      import(
        '@/pages/IndividualOfferSummary/IndividualOfferSummaryPriceCategories/IndividualOfferSummaryPriceCategories'
      ),
    path: '/offre/individuelle/:offerId/tarifs',
    title: 'Tarifs - Consulter une offre individuelle',
  },
  // Stocks pages
  {
    lazy: () => import('@/pages/IndividualOfferWizard/Stocks/Stocks'),
    path: '/offre/individuelle/:offerId/creation/stocks',
    title: 'Stocks et prix - Créer une offre individuelle',
  },
  {
    lazy: () => import('@/pages/IndividualOfferWizard/Stocks/Stocks'),
    path: '/offre/individuelle/:offerId/edition/stocks',
    title: 'Stocks et prix - Modifier une offre individuelle',
  },
  {
    lazy: () =>
      import(
        '@/pages/IndividualOfferSummary/IndividualOfferSummaryStocks/IndividualOfferSummaryStocks'
      ),
    path: '/offre/individuelle/:offerId/stocks',
    title: 'Stocks et prix - Consulter une offre individuelle',
  },
  // Booking summary page
  {
    lazy: () =>
      import(
        '@/pages/IndividualOfferSummary/IndividualOfferSummaryBookings/IndividualOfferSummaryBookings'
      ),
    path: '/offre/individuelle/:offerId/reservations',
    title: 'Réservations - Consulter une offre individuelle',
  },
  // Confirmation pages
  {
    lazy: () =>
      import(
        '@/pages/IndividualOffer/IndividualOfferConfirmation/IndividualOfferConfirmation'
      ),
    path: '/offre/individuelle/:offerId/creation/confirmation',
    title: 'Confirmation - Offre individuelle publiée',
  },
  {
    lazy: () =>
      import(
        '@/pages/IndividualOffer/IndividualOfferConfirmation/IndividualOfferConfirmation'
      ),
    path: '/offre/individuelle/:offerId/confirmation',
    title: 'Confirmation - Offre individuelle publiée',
  },
  // Summary pages
  {
    lazy: () =>
      import(
        '@/pages/IndividualOfferSummary/IndividualOfferSummary/IndividualOfferSummary'
      ),
    path: '/offre/individuelle/:offerId/creation/recapitulatif',
    title: 'Récapitulatif - Créer une offre individuelle',
  },
  {
    lazy: () =>
      import(
        '@/pages/IndividualOfferSummary/IndividualOfferSummary/IndividualOfferSummary'
      ),
    path: '/offre/individuelle/:offerId/recapitulatif',
    title: 'Récapitulatif - Modifier une offre individuelle',
  },
]

export const routesOnboardingIndividualOfferWizard: RouteConfig[] = [
  // details pages
  {
    lazy: () =>
      import(
        '@/pages/IndividualOffer/IndividualOfferDetails/IndividualOfferDetails'
      ),
    path: '/onboarding/offre/individuelle/creation/details',
    title: 'Détails de l’offre - Créer une offre individuelle - Onboarding',
    featureName: 'WIP_ENABLE_PRO_DIDACTIC_ONBOARDING',
  },
  {
    lazy: () =>
      import(
        '@/pages/IndividualOffer/IndividualOfferDetails/IndividualOfferDetails'
      ),
    path: '/onboarding/offre/individuelle/:offerId/creation/details',
    title: 'Détails de l’offre - Créer une offre individuelle - Onboarding',
    featureName: 'WIP_ENABLE_PRO_DIDACTIC_ONBOARDING',
  },
  {
    lazy: () =>
      import(
        '@/pages/IndividualOffer/IndividualOfferInformations/IndividualOfferInformations'
      ),
    path: '/onboarding/offre/individuelle/:offerId/creation/pratiques',
    title: 'Informations pratiques - Créer une offre individuelle - Onboarding',
    featureName: 'WIP_ENABLE_PRO_DIDACTIC_ONBOARDING',
  },
  {
    lazy: () =>
      import('@/pages/IndividualOfferWizard/PriceCategories/PriceCategories'),
    path: '/onboarding/offre/individuelle/:offerId/creation/tarifs',
    featureName: 'WIP_ENABLE_PRO_DIDACTIC_ONBOARDING',
    title: 'Tarifs - Créer une offre individuelle - Onboarding',
  },
  {
    lazy: () => import('@/pages/IndividualOfferWizard/Stocks/Stocks'),
    path: '/onboarding/offre/individuelle/:offerId/creation/stocks',
    title: 'Stocks et prix - Créer une offre individuelle - Onboarding',
    featureName: 'WIP_ENABLE_PRO_DIDACTIC_ONBOARDING',
  },
  {
    lazy: () =>
      import(
        '@/pages/IndividualOfferSummary/IndividualOfferSummary/IndividualOfferSummary'
      ),
    path: '/onboarding/offre/individuelle/:offerId/creation/recapitulatif',
    title: 'Récapitulatif - Créer une offre individuelle - Onboarding',
    featureName: 'WIP_ENABLE_PRO_DIDACTIC_ONBOARDING',
  },
]
