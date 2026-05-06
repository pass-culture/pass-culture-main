/* No need to test this file */
/* istanbul ignore file */
import { withUserPermissions } from '@/commons/auth/withUserPermissions'

import type { CustomRouteGroupChild } from './types'
import {
  mustBeOnboardedWithSelectedPartnerVenue,
  mustNotBeOnboardedWithSelectedPartnerVenue,
} from './utils'

export const routesIndividualOfferWizard: CustomRouteGroupChild[] = [
  {
    lazy: () =>
      import(
        '@/pages/IndividualOffer/IndividualOfferDescription/IndividualOfferDescription'
      ),
    path: '/offre/individuelle/:offerId/edition/details',
    handle: {
      title: 'Détails de l’offre - Modifier une offre individuelle',
    },
    loader: withUserPermissions(mustBeOnboardedWithSelectedPartnerVenue),
  },
  {
    lazy: () =>
      import(
        '@/pages/IndividualOfferSummary/IndividualOfferSummaryDetails/IndividualOfferSummaryDetails'
      ),
    path: '/offre/individuelle/:offerId/recapitulatif/description',
    handle: {
      title: 'Détails de l’offre - Consulter une offre individuelle',
    },
    loader: withUserPermissions(mustBeOnboardedWithSelectedPartnerVenue),
  },
  //  Description
  {
    lazy: () =>
      import(
        '@/pages/IndividualOffer/IndividualOfferDescription/IndividualOfferDescription'
      ),
    path: '/offre/individuelle/creation/description',
    handle: {
      title: 'Description - Créer une offre individuelle',
    },
    loader: withUserPermissions(mustBeOnboardedWithSelectedPartnerVenue),
  },
  {
    lazy: () =>
      import(
        '@/pages/IndividualOffer/IndividualOfferDescription/IndividualOfferDescription'
      ),
    path: '/offre/individuelle/:offerId/creation/description',
    handle: {
      title: 'Description - Créer une offre individuelle',
    },
    loader: withUserPermissions(mustBeOnboardedWithSelectedPartnerVenue),
  },
  {
    lazy: () =>
      import(
        '@/pages/IndividualOffer/IndividualOfferDescription/IndividualOfferDescription'
      ),
    path: '/offre/individuelle/:offerId/edition/description',
    handle: {
      title: 'Description - Modifier une offre individuelle',
    },
    loader: withUserPermissions(mustBeOnboardedWithSelectedPartnerVenue),
  },
  {
    lazy: () =>
      import(
        '@/pages/IndividualOfferSummary/IndividualOfferSummaryDetails/IndividualOfferSummaryDetails'
      ),
    path: '/offre/individuelle/:offerId/recapitulatif/description',
    handle: {
      title: 'Description - Consulter une offre individuelle',
    },
    loader: withUserPermissions(mustBeOnboardedWithSelectedPartnerVenue),
  },
  //  Informations pratiques
  {
    lazy: () =>
      import(
        '@/pages/IndividualOffer/IndividualOfferLocation/IndividualOfferLocation'
      ),
    path: '/offre/individuelle/:offerId/creation/pratiques',
    handle: {
      title: 'Informations pratiques - Créer une offre individuelle',
    },
    loader: withUserPermissions(mustBeOnboardedWithSelectedPartnerVenue),
  },
  {
    lazy: () =>
      import(
        '@/pages/IndividualOffer/IndividualOfferLocation/IndividualOfferLocation'
      ),
    path: '/offre/individuelle/:offerId/edition/pratiques',
    handle: {
      title: 'Informations pratiques - Modifier une offre individuelle',
    },
    loader: withUserPermissions(mustBeOnboardedWithSelectedPartnerVenue),
  },
  //  Location
  {
    lazy: () =>
      import(
        '@/pages/IndividualOffer/IndividualOfferLocation/IndividualOfferLocation'
      ),
    path: '/offre/individuelle/:offerId/creation/localisation',
    handle: {
      title: 'Localisation - Créer une offre individuelle',
    },
    loader: withUserPermissions(mustBeOnboardedWithSelectedPartnerVenue),
  },
  {
    lazy: () =>
      import(
        '@/pages/IndividualOffer/IndividualOfferLocation/IndividualOfferLocation'
      ),
    path: '/offre/individuelle/:offerId/edition/localisation',
    handle: {
      title: 'Localisation - Modifier une offre individuelle',
    },
    loader: withUserPermissions(mustBeOnboardedWithSelectedPartnerVenue),
  },
  {
    lazy: () =>
      import(
        '@/pages/IndividualOfferSummary/IndividualOfferSummaryLocation/IndividualOfferSummaryLocation'
      ),
    path: '/offre/individuelle/:offerId/localisation',
    handle: {
      title: 'Localisation - Consulter une offre individuelle',
    },
    loader: withUserPermissions(mustBeOnboardedWithSelectedPartnerVenue),
  },
  // Image & video (media) pages
  {
    lazy: () =>
      import(
        '@/pages/IndividualOffer/IndividualOfferMedia/IndividualOfferMedia'
      ),
    path: '/offre/individuelle/:offerId/creation/media',
    handle: {
      title: 'Image et vidéo - Créer une offre individuelle',
    },
    loader: withUserPermissions(mustBeOnboardedWithSelectedPartnerVenue),
  },
  {
    lazy: () =>
      import(
        '@/pages/IndividualOffer/IndividualOfferMedia/IndividualOfferMedia'
      ),
    path: '/offre/individuelle/:offerId/edition/media',
    handle: {
      title: 'Image et vidéo - Modifier une offre individuelle',
    },
    loader: withUserPermissions(mustBeOnboardedWithSelectedPartnerVenue),
  },
  {
    lazy: () =>
      import(
        '@/pages/IndividualOfferSummary/IndividualOfferSummaryMedia/IndividualOfferSummaryMedia'
      ),
    path: '/offre/individuelle/:offerId/media',
    handle: {
      title: 'Image et vidéo - Consulter une offre individuelle',
    },
    loader: withUserPermissions(mustBeOnboardedWithSelectedPartnerVenue),
  },
  // Price categories pages
  {
    lazy: () =>
      import(
        '@/pages/IndividualOffer/IndividualOfferPriceTable/IndividualOfferPriceTable'
      ),
    path: '/offre/individuelle/:offerId/creation/tarifs',
    handle: {
      title: 'Tarifs - Créer une offre individuelle',
    },
    loader: withUserPermissions(mustBeOnboardedWithSelectedPartnerVenue),
  },
  {
    lazy: () =>
      import(
        '@/pages/IndividualOffer/IndividualOfferPriceTable/IndividualOfferPriceTable'
      ),
    path: '/offre/individuelle/:offerId/edition/tarifs',
    handle: {
      title: 'Tarifs - Modifier une offre individuelle',
    },
    loader: withUserPermissions(mustBeOnboardedWithSelectedPartnerVenue),
  },
  {
    lazy: () =>
      import(
        '@/pages/IndividualOfferSummary/IndividualOfferSummaryPriceCategories/IndividualOfferSummaryPriceCategories'
      ),
    path: '/offre/individuelle/:offerId/tarifs',
    handle: {
      title: 'Tarifs - Consulter une offre individuelle',
    },
    loader: withUserPermissions(mustBeOnboardedWithSelectedPartnerVenue),
  },
  // Timetable
  {
    lazy: () =>
      import(
        '@/pages/IndividualOffer/IndividualOfferTimetable/IndividualOfferTimetable'
      ),
    path: '/offre/individuelle/:offerId/creation/horaires',
    handle: {
      title: 'Horaires - Créer une offre individuelle',
    },
    loader: withUserPermissions(mustBeOnboardedWithSelectedPartnerVenue),
  },
  {
    lazy: () =>
      import(
        '@/pages/IndividualOffer/IndividualOfferTimetable/IndividualOfferTimetable'
      ),
    path: '/offre/individuelle/:offerId/edition/horaires',
    handle: {
      title: 'Horaires - Modifier une offre individuelle',
    },
    loader: withUserPermissions(mustBeOnboardedWithSelectedPartnerVenue),
  },
  {
    lazy: () =>
      import(
        '@/pages/IndividualOfferSummary/IndividualOfferSummaryStocks/IndividualOfferSummaryStocks'
      ),
    path: '/offre/individuelle/:offerId/horaires',
    handle: {
      title: 'Horaires - Consulter une offre individuelle',
    },
    loader: withUserPermissions(mustBeOnboardedWithSelectedPartnerVenue),
  },
  {
    lazy: () =>
      import(
        '@/pages/IndividualOffer/IndividualOfferPracticalInfos/IndividualOfferPracticalInfos'
      ),
    path: '/offre/individuelle/:offerId/creation/informations_pratiques',
    handle: {
      title: 'Informations pratiques - Créer une offre individuelle',
    },
    loader: withUserPermissions(mustBeOnboardedWithSelectedPartnerVenue),
  },
  {
    lazy: () =>
      import(
        '@/pages/IndividualOffer/IndividualOfferPracticalInfos/IndividualOfferPracticalInfos'
      ),
    path: '/offre/individuelle/:offerId/edition/informations_pratiques',
    handle: {
      title: 'Informations pratiques - Modifier une offre individuelle',
    },
    loader: withUserPermissions(mustBeOnboardedWithSelectedPartnerVenue),
  },
  {
    lazy: () =>
      import(
        '@/pages/IndividualOfferSummary/IndividualOfferSummaryPracticalInfos/IndividualOfferSummaryPracticalInfos'
      ),
    path: '/offre/individuelle/:offerId/informations_pratiques',
    handle: {
      title: 'Informations pratiques - Consulter une offre individuelle',
    },
    loader: withUserPermissions(mustBeOnboardedWithSelectedPartnerVenue),
  },
  // Booking summary page
  {
    lazy: () =>
      import(
        '@/pages/IndividualOfferSummary/IndividualOfferSummaryBookings/IndividualOfferSummaryBookings'
      ),
    path: '/offre/individuelle/:offerId/reservations',
    handle: {
      title: 'Réservations - Consulter une offre individuelle',
    },
    loader: withUserPermissions(mustBeOnboardedWithSelectedPartnerVenue),
  },
  // Confirmation pages
  {
    lazy: () =>
      import(
        '@/pages/IndividualOffer/IndividualOfferConfirmation/IndividualOfferConfirmation'
      ),
    path: '/offre/individuelle/:offerId/creation/confirmation',
    handle: {
      title: 'Confirmation - Offre individuelle publiée',
    },
    loader: withUserPermissions(mustBeOnboardedWithSelectedPartnerVenue),
  },
  // Summary pages
  {
    lazy: () =>
      import(
        '@/pages/IndividualOffer/IndividualOfferSummary/IndividualOfferSummary'
      ),
    path: '/offre/individuelle/:offerId/creation/recapitulatif',
    handle: {
      title: 'Récapitulatif - Créer une offre individuelle',
    },
    loader: withUserPermissions(mustBeOnboardedWithSelectedPartnerVenue),
  },
]

export const routesOnboardingIndividualOfferWizard: CustomRouteGroupChild[] = [
  //  Description
  {
    lazy: () =>
      import(
        '@/pages/IndividualOffer/IndividualOfferDescription/IndividualOfferDescription'
      ),
    path: '/onboarding/offre/individuelle/creation/description',
    handle: {
      title: 'Description - Créer une offre individuelle - Onboarding',
    },
    loader: withUserPermissions(mustNotBeOnboardedWithSelectedPartnerVenue),
  },
  {
    lazy: () =>
      import(
        '@/pages/IndividualOffer/IndividualOfferDescription/IndividualOfferDescription'
      ),
    path: '/onboarding/offre/individuelle/:offerId/creation/description',
    handle: {
      title: 'Description - Créer une offre individuelle - Onboarding',
    },
    loader: withUserPermissions(mustNotBeOnboardedWithSelectedPartnerVenue),
  },
  {
    lazy: () =>
      import(
        '@/pages/IndividualOffer/IndividualOfferLocation/IndividualOfferLocation'
      ),
    path: '/onboarding/offre/individuelle/:offerId/creation/pratiques',
    handle: {
      title:
        'Informations pratiques - Créer une offre individuelle - Onboarding',
    },
    loader: withUserPermissions(mustNotBeOnboardedWithSelectedPartnerVenue),
  },
  //  Localisation
  {
    lazy: () =>
      import(
        '@/pages/IndividualOffer/IndividualOfferLocation/IndividualOfferLocation'
      ),
    path: '/onboarding/offre/individuelle/:offerId/creation/localisation',
    handle: {
      title: 'Localisation - Créer une offre individuelle - Onboarding',
    },
    loader: withUserPermissions(mustNotBeOnboardedWithSelectedPartnerVenue),
  },
  {
    lazy: () =>
      import(
        '@/pages/IndividualOffer/IndividualOfferMedia/IndividualOfferMedia'
      ),
    path: '/onboarding/offre/individuelle/:offerId/creation/media',
    handle: {
      title: 'Image et vidéo - Créer une offre individuelle - Onboarding',
    },
    loader: withUserPermissions(mustNotBeOnboardedWithSelectedPartnerVenue),
  },
  {
    lazy: () =>
      import(
        '@/pages/IndividualOffer/IndividualOfferPriceTable/IndividualOfferPriceTable'
      ),
    path: '/onboarding/offre/individuelle/:offerId/creation/tarifs',
    handle: {
      title: 'Tarifs - Créer une offre individuelle - Onboarding',
    },
    loader: withUserPermissions(mustNotBeOnboardedWithSelectedPartnerVenue),
  },
  {
    lazy: () =>
      import(
        '@/pages/IndividualOffer/IndividualOfferPracticalInfos/IndividualOfferPracticalInfos'
      ),
    path: '/onboarding/offre/individuelle/:offerId/creation/informations_pratiques',
    handle: {
      title:
        'Informations pratiques - Créer une offre individuelle - Onboarding',
    },
    loader: withUserPermissions(mustNotBeOnboardedWithSelectedPartnerVenue),
  },
  //  Stocks
  {
    lazy: () =>
      import(
        '@/pages/IndividualOffer/IndividualOfferTimetable/IndividualOfferTimetable'
      ),
    path: '/onboarding/offre/individuelle/:offerId/creation/stocks',
    handle: {
      title: 'Stocks et prix - Créer une offre individuelle - Onboarding',
    },
    loader: withUserPermissions(mustNotBeOnboardedWithSelectedPartnerVenue),
  },
  //  Timetable
  {
    lazy: () =>
      import(
        '@/pages/IndividualOffer/IndividualOfferTimetable/IndividualOfferTimetable'
      ),
    path: '/onboarding/offre/individuelle/:offerId/creation/horaires',
    handle: {
      title: 'Horaires - Créer une offre individuelle - Onboarding',
    },
    loader: withUserPermissions(mustNotBeOnboardedWithSelectedPartnerVenue),
  },
  {
    lazy: () =>
      import(
        '@/pages/IndividualOffer/IndividualOfferSummary/IndividualOfferSummary'
      ),
    path: '/onboarding/offre/individuelle/:offerId/creation/recapitulatif',
    handle: {
      title: 'Récapitulatif - Créer une offre individuelle - Onboarding',
    },
    loader: withUserPermissions(mustNotBeOnboardedWithSelectedPartnerVenue),
  },
]
