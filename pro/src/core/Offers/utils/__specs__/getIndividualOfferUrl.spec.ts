import { OFFER_WIZARD_STEP_IDS } from 'components/IndividualOfferBreadcrumb/constants'
import { OFFER_WIZARD_MODE } from 'core/Offers/constants'

import { getIndividualOfferUrl } from '../getIndividualOfferUrl'

describe('getIndividualOfferUrl', () => {
  const offerId = 42
  const testCases = [
    // when no offer (mode is no relevant)
    {
      props: {
        offerId: undefined,
        mode: OFFER_WIZARD_MODE.CREATION,
        step: OFFER_WIZARD_STEP_IDS.INFORMATIONS,
      },
      expectedUrl: '/offre/individuelle/creation/informations',
    },
    // when creation mode
    {
      props: {
        offerId: offerId,
        mode: OFFER_WIZARD_MODE.CREATION,
        step: OFFER_WIZARD_STEP_IDS.INFORMATIONS,
      },
      expectedUrl: '/offre/individuelle/42/creation/informations',
    },
    {
      props: {
        offerId: offerId,
        mode: OFFER_WIZARD_MODE.CREATION,
        step: OFFER_WIZARD_STEP_IDS.STOCKS,
      },
      expectedUrl: '/offre/individuelle/42/creation/stocks',
    },
    {
      props: {
        offerId: offerId,
        mode: OFFER_WIZARD_MODE.CREATION,
        step: OFFER_WIZARD_STEP_IDS.SUMMARY,
      },
      expectedUrl: '/offre/individuelle/42/creation/recapitulatif',
    },
    {
      props: {
        offerId: offerId,
        mode: OFFER_WIZARD_MODE.CREATION,
        step: OFFER_WIZARD_STEP_IDS.CONFIRMATION,
      },
      expectedUrl: '/offre/individuelle/42/creation/confirmation',
    },
    {
      props: {
        offerId: offerId,
        mode: OFFER_WIZARD_MODE.CREATION,
        step: OFFER_WIZARD_STEP_IDS.TARIFS,
      },
      expectedUrl: '/offre/individuelle/42/creation/tarifs',
    },
    // when brouillon mode
    {
      props: {
        offerId: offerId,
        mode: OFFER_WIZARD_MODE.DRAFT,
        step: OFFER_WIZARD_STEP_IDS.INFORMATIONS,
      },
      expectedUrl: '/offre/individuelle/42/brouillon/informations',
    },
    {
      props: {
        offerId: offerId,
        mode: OFFER_WIZARD_MODE.DRAFT,
        step: OFFER_WIZARD_STEP_IDS.STOCKS,
      },
      expectedUrl: '/offre/individuelle/42/brouillon/stocks',
    },
    {
      props: {
        offerId: offerId,
        mode: OFFER_WIZARD_MODE.DRAFT,
        step: OFFER_WIZARD_STEP_IDS.SUMMARY,
      },
      expectedUrl: '/offre/individuelle/42/brouillon/recapitulatif',
    },
    {
      props: {
        offerId: offerId,
        mode: OFFER_WIZARD_MODE.DRAFT,
        step: OFFER_WIZARD_STEP_IDS.CONFIRMATION,
      },
      expectedUrl: '/offre/individuelle/42/brouillon/confirmation',
    },

    {
      props: {
        offerId: offerId,
        mode: OFFER_WIZARD_MODE.DRAFT,
        step: OFFER_WIZARD_STEP_IDS.TARIFS,
      },
      expectedUrl: '/offre/individuelle/42/brouillon/tarifs',
    },
    // when edition mode
    {
      props: {
        offerId: offerId,
        mode: OFFER_WIZARD_MODE.EDITION,
        step: OFFER_WIZARD_STEP_IDS.INFORMATIONS,
      },
      expectedUrl: '/offre/individuelle/42/edition/informations',
    },
    {
      props: {
        offerId: offerId,
        mode: OFFER_WIZARD_MODE.EDITION,
        step: OFFER_WIZARD_STEP_IDS.STOCKS,
      },
      expectedUrl: '/offre/individuelle/42/edition/stocks',
    },
    {
      props: {
        offerId: offerId,
        mode: OFFER_WIZARD_MODE.EDITION,
        step: OFFER_WIZARD_STEP_IDS.TARIFS,
      },
      expectedUrl: '/offre/individuelle/42/edition/tarifs',
    },
    // when readonly mode
    {
      props: {
        offerId: offerId,
        mode: OFFER_WIZARD_MODE.READ_ONLY,
        step: OFFER_WIZARD_STEP_IDS.STOCKS,
      },
      expectedUrl: '/offre/individuelle/42/stocks',
    },
    {
      props: {
        offerId: offerId,
        mode: OFFER_WIZARD_MODE.READ_ONLY,
        step: OFFER_WIZARD_STEP_IDS.SUMMARY,
      },
      expectedUrl: '/offre/individuelle/42/recapitulatif',
    },
    {
      props: {
        offerId: offerId,
        mode: OFFER_WIZARD_MODE.READ_ONLY,
        step: OFFER_WIZARD_STEP_IDS.CONFIRMATION,
      },
      expectedUrl: '',
    },
    {
      props: {
        offerId: offerId,
        mode: OFFER_WIZARD_MODE.READ_ONLY,
        step: OFFER_WIZARD_STEP_IDS.TARIFS,
      },
      expectedUrl: '/offre/individuelle/42/tarifs',
    },
    {
      props: {
        offerId: offerId,
        mode: OFFER_WIZARD_MODE.READ_ONLY,
        step: OFFER_WIZARD_STEP_IDS.BOOKINGS,
      },
      expectedUrl: '/offre/individuelle/42/reservations',
    },
  ]
  it.each(testCases)('should return right url', ({ props, expectedUrl }) => {
    expect(getIndividualOfferUrl(props)).toBe(expectedUrl)
  })
})
