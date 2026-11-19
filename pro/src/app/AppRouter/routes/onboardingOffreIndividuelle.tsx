import { withUserPermissions } from '@/commons/auth/withUserPermissions'

import type { CustomRouteGroupChild } from '../types'
import { mustNotBeOnboardedWithSelectedPartnerVenue } from '../utils'

export const ONBOARDING_OFFRE_INDIVIDUELLE_ROUTES = {
  ONBOARDING_OFFRE_INDIVIDUELLE: '/onboarding/offre/individuelle',
  ONBOARDING_OFFRE_INDIVIDUELLE_CREATION_DESCRIPTION:
    '/onboarding/offre/individuelle/creation/description',
  ONBOARDING_OFFRE_INDIVIDUELLE_ID_CREATION_DESCRIPTION:
    '/onboarding/offre/individuelle/:offerId/creation/description',
  ONBOARDING_OFFRE_INDIVIDUELLE_ID_CREATION_PRATIQUES:
    '/onboarding/offre/individuelle/:offerId/creation/pratiques',
  ONBOARDING_OFFRE_INDIVIDUELLE_ID_CREATION_LOCALISATION:
    '/onboarding/offre/individuelle/:offerId/creation/localisation',
  ONBOARDING_OFFRE_INDIVIDUELLE_ID_CREATION_MEDIA:
    '/onboarding/offre/individuelle/:offerId/creation/media',
  ONBOARDING_OFFRE_INDIVIDUELLE_ID_CREATION_TARIFS:
    '/onboarding/offre/individuelle/:offerId/creation/tarifs',
  ONBOARDING_OFFRE_INDIVIDUELLE_ID_CREATION_INFORMATIONS_PRATIQUES:
    '/onboarding/offre/individuelle/:offerId/creation/informations_pratiques',
  ONBOARDING_OFFRE_INDIVIDUELLE_ID_CREATION_STOCKS:
    '/onboarding/offre/individuelle/:offerId/creation/stocks',
  ONBOARDING_OFFRE_INDIVIDUELLE_ID_CREATION_HORAIRES:
    '/onboarding/offre/individuelle/:offerId/creation/horaires',
  ONBOARDING_OFFRE_INDIVIDUELLE_ID_CREATION_RECAPITULATIF:
    '/onboarding/offre/individuelle/:offerId/creation/recapitulatif',
} as const

export const onboardingOffreIndividuelleRoutes: CustomRouteGroupChild[] = [
  //  Description
  {
    lazy: () =>
      import(
        '@/pages/IndividualOffer/IndividualOfferDescription/IndividualOfferDescription'
      ),
    path: 'creation/description',
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
    path: ':offerId/creation/description',
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
    path: ':offerId/creation/pratiques',
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
    path: ':offerId/creation/localisation',
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
    path: ':offerId/creation/media',
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
    path: ':offerId/creation/tarifs',
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
    path: ':offerId/creation/informations_pratiques',
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
    path: ':offerId/creation/stocks',
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
    path: ':offerId/creation/horaires',
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
    path: ':offerId/creation/recapitulatif',
    handle: {
      title: 'Récapitulatif - Créer une offre individuelle - Onboarding',
    },
    loader: withUserPermissions(mustNotBeOnboardedWithSelectedPartnerVenue),
  },
]
