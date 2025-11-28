/* No need to test this file */
/* istanbul ignore file */
import type { CustomRouteObject } from './types'

export const routesIndividualOfferWizard: CustomRouteObject[] = [
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
    path: '/offre/individuelle/:offerId/recapitulatif/description',
    title: 'Détails de l’offre - Consulter une offre individuelle',
  },
  //  Description
  {
    lazy: () =>
      import(
        '@/pages/IndividualOffer/IndividualOfferDetails/IndividualOfferDetails'
      ),
    path: '/offre/individuelle/creation/description',
    title: 'Description - Créer une offre individuelle',
  },
  {
    lazy: () =>
      import(
        '@/pages/IndividualOffer/IndividualOfferDetails/IndividualOfferDetails'
      ),
    path: '/offre/individuelle/:offerId/creation/description',
    title: 'Description - Créer une offre individuelle',
  },
  {
    lazy: () =>
      import(
        '@/pages/IndividualOffer/IndividualOfferDetails/IndividualOfferDetails'
      ),
    path: '/offre/individuelle/:offerId/edition/description',
    title: 'Description - Modifier une offre individuelle',
  },
  {
    lazy: () =>
      import(
        '@/pages/IndividualOfferSummary/IndividualOfferSummaryDetails/IndividualOfferSummaryDetails'
      ),
    path: '/offre/individuelle/:offerId/recapitulatif/description',
    title: 'Description - Consulter une offre individuelle',
  },
  //  Informations pratiques
  {
    lazy: () =>
      import(
        '@/pages/IndividualOffer/IndividualOfferLocation/IndividualOfferLocation'
      ),
    path: '/offre/individuelle/:offerId/creation/pratiques',
    title: 'Informations pratiques - Créer une offre individuelle',
  },
  {
    lazy: () =>
      import(
        '@/pages/IndividualOffer/IndividualOfferLocation/IndividualOfferLocation'
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
  //  Localisation
  {
    lazy: () =>
      import(
        '@/pages/IndividualOffer/IndividualOfferLocation/IndividualOfferLocation'
      ),
    path: '/offre/individuelle/:offerId/creation/localisation',
    title: 'Localisation - Créer une offre individuelle',
  },
  {
    lazy: () =>
      import(
        '@/pages/IndividualOffer/IndividualOfferLocation/IndividualOfferLocation'
      ),
    path: '/offre/individuelle/:offerId/edition/localisation',
    title: 'Localisation - Modifier une offre individuelle',
  },
  {
    lazy: () =>
      import(
        '@/pages/IndividualOfferSummary/IndividualOfferSummaryInformations/IndividualOfferSummaryInformations'
      ),
    path: '/offre/individuelle/:offerId/localisation',
    title: 'Localisation - Consulter une offre individuelle',
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
      import(
        '@/pages/IndividualOffer/IndividualOfferPriceTable/IndividualOfferPriceTable'
      ),
    path: '/offre/individuelle/:offerId/creation/tarifs',
    title: 'Tarifs - Créer une offre individuelle',
  },
  {
    lazy: () =>
      import(
        '@/pages/IndividualOffer/IndividualOfferPriceTable/IndividualOfferPriceTable'
      ),
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
  // Timetable
  {
    lazy: () =>
      import(
        '@/pages/IndividualOffer/IndividualOfferTimetable/IndividualOfferTimetable'
      ),
    path: '/offre/individuelle/:offerId/creation/horaires',
    title: 'Horaires - Créer une offre individuelle',
  },
  {
    lazy: () =>
      import(
        '@/pages/IndividualOffer/IndividualOfferTimetable/IndividualOfferTimetable'
      ),
    path: '/offre/individuelle/:offerId/edition/horaires',
    title: 'Horaires - Modifier une offre individuelle',
  },
  {
    lazy: () =>
      import(
        '@/pages/IndividualOfferSummary/IndividualOfferSummaryStocks/IndividualOfferSummaryStocks'
      ),
    path: '/offre/individuelle/:offerId/horaires',
    title: 'Horaires - Consulter une offre individuelle',
  },
  {
    lazy: () =>
      import(
        '@/pages/IndividualOffer/IndividualOfferPracticalInfos/IndividualOfferPracticalInfos'
      ),
    path: '/offre/individuelle/:offerId/creation/informations_pratiques',
    title: 'Informations pratiques - Créer une offre individuelle',
  },
  {
    lazy: () =>
      import(
        '@/pages/IndividualOffer/IndividualOfferPracticalInfos/IndividualOfferPracticalInfos'
      ),
    path: '/offre/individuelle/:offerId/edition/informations_pratiques',
    title: 'Informations pratiques - Modifier une offre individuelle',
  },
  {
    lazy: () =>
      import(
        '@/pages/IndividualOfferSummary/IndividualOfferSummaryPracticalInfos/IndividualOfferSummaryPracticalInfos'
      ),
    path: '/offre/individuelle/:offerId/informations_pratiques',
    title: 'Informations pratiques - Consulter une offre individuelle',
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
  // Summary pages
  {
    lazy: () =>
      import(
        '@/pages/IndividualOffer/IndividualOfferSummary/IndividualOfferSummary'
      ),
    path: '/offre/individuelle/:offerId/creation/recapitulatif',
    title: 'Récapitulatif - Créer une offre individuelle',
  },
]

export const routesOnboardingIndividualOfferWizard: CustomRouteObject[] = [
  // details pages
  {
    lazy: () =>
      import(
        '@/pages/IndividualOffer/IndividualOfferDetails/IndividualOfferDetails'
      ),
    path: '/onboarding/offre/individuelle/creation/details',
    title: 'Détails de l’offre - Créer une offre individuelle - Onboarding',
    meta: {
      onboardingOnly: true,
    },
  },
  {
    lazy: () =>
      import(
        '@/pages/IndividualOffer/IndividualOfferDetails/IndividualOfferDetails'
      ),
    path: '/onboarding/offre/individuelle/:offerId/creation/details',
    title: 'Détails de l’offre - Créer une offre individuelle - Onboarding',
    meta: {
      onboardingOnly: true,
    },
  },
  //  Description
  {
    lazy: () =>
      import(
        '@/pages/IndividualOffer/IndividualOfferDetails/IndividualOfferDetails'
      ),
    path: '/onboarding/offre/individuelle/creation/description',
    title: 'Description - Créer une offre individuelle - Onboarding',
    meta: {
      onboardingOnly: true,
    },
  },
  {
    lazy: () =>
      import(
        '@/pages/IndividualOffer/IndividualOfferDetails/IndividualOfferDetails'
      ),
    path: '/onboarding/offre/individuelle/:offerId/creation/description',
    title: 'Description - Créer une offre individuelle - Onboarding',
    meta: {
      onboardingOnly: true,
    },
  },
  {
    lazy: () =>
      import(
        '@/pages/IndividualOffer/IndividualOfferLocation/IndividualOfferLocation'
      ),
    path: '/onboarding/offre/individuelle/:offerId/creation/pratiques',
    title: 'Informations pratiques - Créer une offre individuelle - Onboarding',
    meta: {
      onboardingOnly: true,
    },
  },
  //  Localisation
  {
    lazy: () =>
      import(
        '@/pages/IndividualOffer/IndividualOfferLocation/IndividualOfferLocation'
      ),
    path: '/onboarding/offre/individuelle/:offerId/creation/localisation',
    title: 'Localisation - Créer une offre individuelle - Onboarding',
    meta: {
      onboardingOnly: true,
    },
  },
  {
    lazy: () =>
      import(
        '@/pages/IndividualOffer/IndividualOfferMedia/IndividualOfferMedia'
      ),
    path: '/onboarding/offre/individuelle/:offerId/creation/media',
    title: 'Image et vidéo - Créer une offre individuelle - Onboarding',
    meta: {
      onboardingOnly: true,
    },
  },
  {
    lazy: () =>
      import(
        '@/pages/IndividualOffer/IndividualOfferPriceTable/IndividualOfferPriceTable'
      ),
    path: '/onboarding/offre/individuelle/:offerId/creation/tarifs',
    title: 'Tarifs - Créer une offre individuelle - Onboarding',
    meta: {
      onboardingOnly: true,
    },
  },
  {
    lazy: () =>
      import(
        '@/pages/IndividualOffer/IndividualOfferPracticalInfos/IndividualOfferPracticalInfos'
      ),
    path: '/onboarding/offre/individuelle/:offerId/creation/informations_pratiques',
    title: 'Informations pratiques - Créer une offre individuelle - Onboarding',
    meta: {
      onboardingOnly: true,
    },
  },
  //  Stocks
  {
    lazy: () =>
      import(
        '@/pages/IndividualOffer/IndividualOfferTimetable/IndividualOfferTimetable'
      ),
    path: '/onboarding/offre/individuelle/:offerId/creation/stocks',
    title: 'Stocks et prix - Créer une offre individuelle - Onboarding',
    meta: {
      onboardingOnly: true,
    },
  },
  //  Timetable
  {
    lazy: () =>
      import(
        '@/pages/IndividualOffer/IndividualOfferTimetable/IndividualOfferTimetable'
      ),
    path: '/onboarding/offre/individuelle/:offerId/creation/horaires',
    title: 'Horaires - Créer une offre individuelle - Onboarding',
    meta: {
      onboardingOnly: true,
    },
  },
  {
    lazy: () =>
      import(
        '@/pages/IndividualOffer/IndividualOfferSummary/IndividualOfferSummary'
      ),
    path: '/onboarding/offre/individuelle/:offerId/creation/recapitulatif',
    title: 'Récapitulatif - Créer une offre individuelle - Onboarding',
    meta: {
      onboardingOnly: true,
    },
  },
]
