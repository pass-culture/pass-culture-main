import { withUserPermissions } from '@/commons/auth/withUserPermissions'

import type { CustomRouteGroupChild } from '../types'
import {
  mustBeOnboardedWithActiveSelectedPartnerVenue,
  mustBeOnboardedWithSelectedPartnerVenue,
} from '../utils'

export const OFFRE_INDIVIDUELLE_ROUTES = {
  OFFRE_INDIVIDUELLE: '/offre/individuelle',
  OFFRE_INDIVIDUELLE_EDITION_DETAILS:
    '/offre/individuelle/:offerId/edition/details',
  OFFRE_INDIVIDUELLE_VISIBILITE: '/offre/individuelle/:offerId/visibilite',
  OFFRE_INDIVIDUELLE_CREATION_DESCRIPTION:
    '/offre/individuelle/creation/description',
  OFFRE_INDIVIDUELLE_ID_CREATION_DESCRIPTION:
    '/offre/individuelle/:offerId/creation/description',
  OFFRE_INDIVIDUELLE_ID_EDITION_DESCRIPTION:
    '/offre/individuelle/:offerId/edition/description',
  OFFRE_INDIVIDUELLE_ID_CREATION_PRATIQUES:
    '/offre/individuelle/:offerId/creation/pratiques',
  OFFRE_INDIVIDUELLE_ID_EDITION_PRATIQUES:
    '/offre/individuelle/:offerId/edition/pratiques',
  OFFRE_INDIVIDUELLE_ID_CREATION_LOCALISATION:
    '/offre/individuelle/:offerId/creation/localisation',
  OFFRE_INDIVIDUELLE_ID_EDITION_LOCALISATION:
    '/offre/individuelle/:offerId/edition/localisation',
  OFFRE_INDIVIDUELLE_ID_CREATION_MEDIA:
    '/offre/individuelle/:offerId/creation/media',
  OFFRE_INDIVIDUELLE_ID_EDITION_MEDIA:
    '/offre/individuelle/:offerId/edition/media',
  OFFRE_INDIVIDUELLE_ID_CREATION_TARIFS:
    '/offre/individuelle/:offerId/creation/tarifs',
  OFFRE_INDIVIDUELLE_ID_EDITION_TARIFS:
    '/offre/individuelle/:offerId/edition/tarifs',
  OFFRE_INDIVIDUELLE_ID_CREATION_HORAIRES:
    '/offre/individuelle/:offerId/creation/horaires',
  OFFRE_INDIVIDUELLE_ID_EDITION_HORAIRES:
    '/offre/individuelle/:offerId/edition/horaires',
  OFFRE_INDIVIDUELLE_ID_CREATION_INFORMATIONS_PRATIQUES:
    '/offre/individuelle/:offerId/creation/informations_pratiques',
  OFFRE_INDIVIDUELLE_ID_EDITION_INFORMATIONS_PRATIQUES:
    '/offre/individuelle/:offerId/edition/informations_pratiques',
  OFFRE_INDIVIDUELLE_ID_RESERVATIONS:
    '/offre/individuelle/:offerId/reservations',
  OFFRE_INDIVIDUELLE_ID_CREATION_CONFIRMATION:
    '/offre/individuelle/:offerId/creation/confirmation',
  OFFRE_INDIVIDUELLE_ID_CREATION_RECAPITULATIF:
    '/offre/individuelle/:offerId/creation/recapitulatif',
} as const

export const offreIndividuelleRoutes: CustomRouteGroupChild[] = [
  {
    lazy: () =>
      import(
        '@/pages/IndividualOffer/IndividualOfferDescription/IndividualOfferDescription'
      ),
    path: ':offerId/edition/details',
    handle: {
      title: 'Détails de l’offre - Modifier une offre individuelle',
    },
    loader: withUserPermissions(mustBeOnboardedWithSelectedPartnerVenue),
  },
  // Exposure
  {
    lazy: () =>
      import(
        '@/pages/IndividualOffer/IndividualOfferExposure/IndividualOfferExposure'
      ),
    path: ':offerId/visibilite',
    handle: {
      title: 'Visibilité - Consulter une offre individuelle',
    },
    loader: withUserPermissions(mustBeOnboardedWithSelectedPartnerVenue),
  },
  //  Description
  {
    lazy: () =>
      import(
        '@/pages/IndividualOffer/IndividualOfferDescription/IndividualOfferDescription'
      ),
    path: 'creation/description',
    handle: {
      title: 'Description - Créer une offre individuelle',
    },
    loader: withUserPermissions(mustBeOnboardedWithActiveSelectedPartnerVenue),
  },
  {
    lazy: () =>
      import(
        '@/pages/IndividualOffer/IndividualOfferDescription/IndividualOfferDescription'
      ),
    path: ':offerId/creation/description',
    handle: {
      title: 'Description - Créer une offre individuelle',
    },
    loader: withUserPermissions(mustBeOnboardedWithActiveSelectedPartnerVenue),
  },
  {
    lazy: () =>
      import(
        '@/pages/IndividualOffer/IndividualOfferDescription/IndividualOfferDescription'
      ),
    path: ':offerId/edition/description',
    handle: {
      title: 'Description - Modifier une offre individuelle',
    },
    loader: withUserPermissions(mustBeOnboardedWithSelectedPartnerVenue),
  },

  //  Practical Informations
  {
    lazy: () =>
      import(
        '@/pages/IndividualOffer/IndividualOfferLocation/IndividualOfferLocation'
      ),
    path: ':offerId/creation/pratiques',
    handle: {
      title: 'Informations pratiques - Créer une offre individuelle',
    },
    loader: withUserPermissions(mustBeOnboardedWithActiveSelectedPartnerVenue),
  },
  {
    lazy: () =>
      import(
        '@/pages/IndividualOffer/IndividualOfferLocation/IndividualOfferLocation'
      ),
    path: ':offerId/edition/pratiques',
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
    path: ':offerId/creation/localisation',
    handle: {
      title: 'Localisation - Créer une offre individuelle',
    },
    loader: withUserPermissions(mustBeOnboardedWithActiveSelectedPartnerVenue),
  },
  {
    lazy: () =>
      import(
        '@/pages/IndividualOffer/IndividualOfferLocation/IndividualOfferLocation'
      ),
    path: ':offerId/edition/localisation',
    handle: {
      title: 'Localisation - Modifier une offre individuelle',
    },
    loader: withUserPermissions(mustBeOnboardedWithSelectedPartnerVenue),
  },
  // Image & video (media) pages
  {
    lazy: () =>
      import(
        '@/pages/IndividualOffer/IndividualOfferMedia/IndividualOfferMedia'
      ),
    path: ':offerId/creation/media',
    handle: {
      title: 'Image et vidéo - Créer une offre individuelle',
    },
    loader: withUserPermissions(mustBeOnboardedWithActiveSelectedPartnerVenue),
  },
  {
    lazy: () =>
      import(
        '@/pages/IndividualOffer/IndividualOfferMedia/IndividualOfferMedia'
      ),
    path: ':offerId/edition/media',
    handle: {
      title: 'Image et vidéo - Modifier une offre individuelle',
    },
    loader: withUserPermissions(mustBeOnboardedWithSelectedPartnerVenue),
  },
  // Price categories pages
  {
    lazy: () =>
      import(
        '@/pages/IndividualOffer/IndividualOfferPriceTable/IndividualOfferPriceTable'
      ),
    path: ':offerId/creation/tarifs',
    handle: {
      title: 'Tarifs - Créer une offre individuelle',
    },
    loader: withUserPermissions(mustBeOnboardedWithActiveSelectedPartnerVenue),
  },
  {
    lazy: () =>
      import(
        '@/pages/IndividualOffer/IndividualOfferPriceTable/IndividualOfferPriceTable'
      ),
    path: ':offerId/edition/tarifs',
    handle: {
      title: 'Tarifs - Modifier une offre individuelle',
    },
    loader: withUserPermissions(mustBeOnboardedWithSelectedPartnerVenue),
  },
  // Timetable
  {
    lazy: () =>
      import(
        '@/pages/IndividualOffer/IndividualOfferTimetable/IndividualOfferTimetable'
      ),
    path: ':offerId/creation/horaires',
    handle: {
      title: 'Horaires - Créer une offre individuelle',
    },
    loader: withUserPermissions(mustBeOnboardedWithActiveSelectedPartnerVenue),
  },
  {
    lazy: () =>
      import(
        '@/pages/IndividualOffer/IndividualOfferTimetable/IndividualOfferTimetable'
      ),
    path: ':offerId/edition/horaires',
    handle: {
      title: 'Horaires - Modifier une offre individuelle',
    },
    loader: withUserPermissions(mustBeOnboardedWithSelectedPartnerVenue),
  },
  {
    lazy: () =>
      import(
        '@/pages/IndividualOffer/IndividualOfferPracticalInfos/IndividualOfferPracticalInfos'
      ),
    path: ':offerId/creation/informations_pratiques',
    handle: {
      title: 'Informations pratiques - Créer une offre individuelle',
    },
    loader: withUserPermissions(mustBeOnboardedWithActiveSelectedPartnerVenue),
  },
  {
    lazy: () =>
      import(
        '@/pages/IndividualOffer/IndividualOfferPracticalInfos/IndividualOfferPracticalInfos'
      ),
    path: ':offerId/edition/informations_pratiques',
    handle: {
      title: 'Informations pratiques - Modifier une offre individuelle',
    },
    loader: withUserPermissions(mustBeOnboardedWithSelectedPartnerVenue),
  },
  // Booking summary page
  {
    lazy: () =>
      import(
        '@/pages/IndividualOfferSummary/IndividualOfferSummaryBookings/IndividualOfferSummaryBookings'
      ),
    path: ':offerId/reservations',
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
    path: ':offerId/creation/confirmation',
    handle: {
      title: 'Confirmation - Offre individuelle publiée',
    },
    loader: withUserPermissions(mustBeOnboardedWithActiveSelectedPartnerVenue),
  },
  // Summary pages
  {
    lazy: () =>
      import(
        '@/pages/IndividualOffer/IndividualOfferSummary/IndividualOfferSummary'
      ),
    path: ':offerId/creation/recapitulatif',
    handle: {
      title: 'Récapitulatif - Créer une offre individuelle',
    },
    loader: withUserPermissions(mustBeOnboardedWithActiveSelectedPartnerVenue),
  },
]
