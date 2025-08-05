import {
  INDIVIDUAL_OFFER_WIZARD_STEP_IDS,
  OFFER_WIZARD_MODE,
} from 'commons/core/Offers/constants'

import { getIndividualOfferUrl } from '../getIndividualOfferUrl'

describe('getIndividualOfferUrl', () => {
  const offerId = 42
  const testCases = [
    // when no offer (mode is no relevant)
    {
      props: {
        offerId: undefined,
        mode: OFFER_WIZARD_MODE.CREATION,
        step: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.DETAILS,
      },
      expectedUrl: '/offre/individuelle/creation/details',
    },
    // when creation mode
    {
      props: {
        offerId: offerId,
        mode: OFFER_WIZARD_MODE.CREATION,
        step: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.DETAILS,
      },
      expectedUrl: '/offre/individuelle/42/creation/details',
    },
    {
      props: {
        offerId: offerId,
        mode: OFFER_WIZARD_MODE.CREATION,
        step: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.STOCKS,
      },
      expectedUrl: '/offre/individuelle/42/creation/stocks',
    },
    {
      props: {
        offerId: offerId,
        mode: OFFER_WIZARD_MODE.CREATION,
        step: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.SUMMARY,
      },
      expectedUrl: '/offre/individuelle/42/creation/recapitulatif',
    },
    {
      props: {
        offerId: offerId,
        mode: OFFER_WIZARD_MODE.CREATION,
        step: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.CONFIRMATION,
      },
      expectedUrl: '/offre/individuelle/42/creation/confirmation',
    },
    {
      props: {
        offerId: offerId,
        mode: OFFER_WIZARD_MODE.CREATION,
        step: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.TARIFS,
      },
      expectedUrl: '/offre/individuelle/42/creation/tarifs',
    },
    // when edition mode
    {
      props: {
        offerId: offerId,
        mode: OFFER_WIZARD_MODE.EDITION,
        step: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.DETAILS,
      },
      expectedUrl: '/offre/individuelle/42/edition/details',
    },
    {
      props: {
        offerId: offerId,
        mode: OFFER_WIZARD_MODE.EDITION,
        step: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.STOCKS,
      },
      expectedUrl: '/offre/individuelle/42/edition/stocks',
    },
    {
      props: {
        offerId: offerId,
        mode: OFFER_WIZARD_MODE.EDITION,
        step: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.TARIFS,
      },
      expectedUrl: '/offre/individuelle/42/edition/tarifs',
    },
    // when readonly mode
    {
      props: {
        offerId: offerId,
        mode: OFFER_WIZARD_MODE.READ_ONLY,
        step: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.STOCKS,
      },
      expectedUrl: '/offre/individuelle/42/stocks',
    },
    {
      props: {
        offerId: offerId,
        mode: OFFER_WIZARD_MODE.READ_ONLY,
        step: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.SUMMARY,
      },
      expectedUrl: '/offre/individuelle/42/recapitulatif',
    },
    {
      props: {
        offerId: offerId,
        mode: OFFER_WIZARD_MODE.READ_ONLY,
        step: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.CONFIRMATION,
      },
      expectedUrl: '',
    },
    {
      props: {
        offerId: offerId,
        mode: OFFER_WIZARD_MODE.READ_ONLY,
        step: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.TARIFS,
      },
      expectedUrl: '/offre/individuelle/42/tarifs',
    },
    {
      props: {
        offerId: offerId,
        mode: OFFER_WIZARD_MODE.READ_ONLY,
        step: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.BOOKINGS,
      },
      expectedUrl: '/offre/individuelle/42/reservations',
    },
  ]
  it.each(testCases)('should return right url', ({ props, expectedUrl }) => {
    expect(getIndividualOfferUrl(props)).toBe(expectedUrl)
  })

  describe('onboarding', () => {
    const onBoardingTestCases = [
      // when no offer (mode is no relevant)
      {
        props: {
          offerId: undefined,
          mode: OFFER_WIZARD_MODE.CREATION,
          step: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.DETAILS,
          isOnboarding: true,
        },
        expectedUrl: '/onboarding/offre/individuelle/creation/details',
      },
      // when creation mode
      {
        props: {
          offerId: offerId,
          mode: OFFER_WIZARD_MODE.CREATION,
          step: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.DETAILS,
          isOnboarding: true,
        },
        expectedUrl: '/onboarding/offre/individuelle/42/creation/details',
      },
      {
        props: {
          offerId: offerId,
          mode: OFFER_WIZARD_MODE.CREATION,
          step: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.STOCKS,
          isOnboarding: true,
        },
        expectedUrl: '/onboarding/offre/individuelle/42/creation/stocks',
      },
      {
        props: {
          offerId: offerId,
          mode: OFFER_WIZARD_MODE.CREATION,
          step: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.SUMMARY,
          isOnboarding: true,
        },
        expectedUrl: '/onboarding/offre/individuelle/42/creation/recapitulatif',
      },
      {
        props: {
          offerId: offerId,
          mode: OFFER_WIZARD_MODE.CREATION,
          step: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.TARIFS,
          isOnboarding: true,
        },
        expectedUrl: '/onboarding/offre/individuelle/42/creation/tarifs',
      },
    ]

    it.each(onBoardingTestCases)(
      'should return right url',
      ({ props, expectedUrl }) => {
        expect(getIndividualOfferUrl(props)).toBe(expectedUrl)
      }
    )
  })
})
