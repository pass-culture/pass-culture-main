import { OFFER_WIZARD_STEP_IDS } from 'components/OfferIndividualStepper'
import { OFFER_WIZARD_MODE } from 'core/Offers'

import getOfferIndividualUrl from '../getOfferIndividualUrl'

describe('getOfferIndividualUrl', () => {
  const propsAndExpectedV3 = [
    // when no offer (mode is no relevant)
    {
      props: {
        offerId: undefined,
        mode: OFFER_WIZARD_MODE.CREATION,
        step: OFFER_WIZARD_STEP_IDS.INFORMATIONS,
        isV2: false,
      },
      expectedUrl: '/offre/v3/creation/individuelle/informations',
    },
    // when creation mode
    {
      props: {
        offerId: '42',
        mode: OFFER_WIZARD_MODE.CREATION,
        step: OFFER_WIZARD_STEP_IDS.INFORMATIONS,
        isV2: false,
      },
      expectedUrl: '/offre/42/v3/creation/individuelle/informations',
    },
    {
      props: {
        offerId: '42',
        mode: OFFER_WIZARD_MODE.CREATION,
        step: OFFER_WIZARD_STEP_IDS.STOCKS,
        isV2: false,
      },
      expectedUrl: '/offre/42/v3/creation/individuelle/stocks',
    },
    {
      props: {
        offerId: '42',
        mode: OFFER_WIZARD_MODE.CREATION,
        step: OFFER_WIZARD_STEP_IDS.SUMMARY,
        isV2: false,
      },
      expectedUrl: '/offre/42/v3/creation/individuelle/recapitulatif',
    },
    {
      props: {
        offerId: '42',
        mode: OFFER_WIZARD_MODE.CREATION,
        step: OFFER_WIZARD_STEP_IDS.CONFIRMATION,
        isV2: false,
      },
      expectedUrl: '/offre/42/v3/creation/individuelle/confirmation',
    },
    // when brouillon mode
    {
      props: {
        offerId: '42',
        mode: OFFER_WIZARD_MODE.DRAFT,
        step: OFFER_WIZARD_STEP_IDS.INFORMATIONS,
        isV2: false,
      },
      expectedUrl: '/offre/42/v3/brouillon/individuelle/informations',
    },
    {
      props: {
        offerId: '42',
        mode: OFFER_WIZARD_MODE.DRAFT,
        step: OFFER_WIZARD_STEP_IDS.STOCKS,
        isV2: false,
      },
      expectedUrl: '/offre/42/v3/brouillon/individuelle/stocks',
    },
    {
      props: {
        offerId: '42',
        mode: OFFER_WIZARD_MODE.DRAFT,
        step: OFFER_WIZARD_STEP_IDS.SUMMARY,
        isV2: false,
      },
      expectedUrl: '/offre/42/v3/brouillon/individuelle/recapitulatif',
    },
    {
      props: {
        offerId: '42',
        mode: OFFER_WIZARD_MODE.DRAFT,
        step: OFFER_WIZARD_STEP_IDS.CONFIRMATION,
        isV2: false,
      },
      expectedUrl: '/offre/42/v3/brouillon/individuelle/confirmation',
    },
    // when edition mode
    {
      props: {
        offerId: '42',
        mode: OFFER_WIZARD_MODE.EDITION,
        step: OFFER_WIZARD_STEP_IDS.INFORMATIONS,
        isV2: false,
      },
      expectedUrl: '/offre/42/v3/individuelle/informations',
    },
    {
      props: {
        offerId: '42',
        mode: OFFER_WIZARD_MODE.EDITION,
        step: OFFER_WIZARD_STEP_IDS.STOCKS,
        isV2: false,
      },
      expectedUrl: '/offre/42/v3/individuelle/stocks',
    },
    {
      props: {
        offerId: '42',
        mode: OFFER_WIZARD_MODE.EDITION,
        step: OFFER_WIZARD_STEP_IDS.SUMMARY,
        isV2: false,
      },
      expectedUrl: '/offre/42/v3/individuelle/recapitulatif',
    },
    {
      props: {
        offerId: '42',
        mode: OFFER_WIZARD_MODE.EDITION,
        step: OFFER_WIZARD_STEP_IDS.CONFIRMATION,
        isV2: false,
      },
      expectedUrl: '',
    },
  ]
  it.each(propsAndExpectedV3)(
    'should return right v3 url',
    propsAndExpectedV3 => {
      const url = getOfferIndividualUrl(propsAndExpectedV3.props)

      expect(url).toBe(propsAndExpectedV3.expectedUrl)
    }
  )

  const propsAndExpectedV2 = [
    // when no offer (mode is no relevant)
    {
      props: {
        offerId: undefined,
        mode: OFFER_WIZARD_MODE.CREATION,
        step: OFFER_WIZARD_STEP_IDS.INFORMATIONS,
        isV2: true,
      },
      expectedUrl: '/offre/creation/individuel',
    },
    // when creation mode
    {
      props: {
        offerId: '42',
        mode: OFFER_WIZARD_MODE.CREATION,
        step: OFFER_WIZARD_STEP_IDS.INFORMATIONS,
        isV2: true,
      },
      expectedUrl: '/offre/42/individuel/creation',
    },
    {
      props: {
        offerId: '42',
        mode: OFFER_WIZARD_MODE.CREATION,
        step: OFFER_WIZARD_STEP_IDS.STOCKS,
        isV2: true,
      },
      expectedUrl: '/offre/42/individuel/creation/stocks',
    },
    {
      props: {
        offerId: '42',
        mode: OFFER_WIZARD_MODE.CREATION,
        step: OFFER_WIZARD_STEP_IDS.SUMMARY,
        isV2: true,
      },
      expectedUrl: '/offre/42/individuel/creation/recapitulatif',
    },
    {
      props: {
        offerId: '42',
        mode: OFFER_WIZARD_MODE.CREATION,
        step: OFFER_WIZARD_STEP_IDS.CONFIRMATION,
        isV2: true,
      },
      expectedUrl: '/offre/42/individuel/creation/confirmation',
    },
    // when brouillon mode
    {
      props: {
        offerId: '42',
        mode: OFFER_WIZARD_MODE.DRAFT,
        step: OFFER_WIZARD_STEP_IDS.INFORMATIONS,
        isV2: true,
      },
      expectedUrl: '/offre/42/individuel/brouillon',
    },
    {
      props: {
        offerId: '42',
        mode: OFFER_WIZARD_MODE.DRAFT,
        step: OFFER_WIZARD_STEP_IDS.STOCKS,
        isV2: true,
      },
      expectedUrl: '/offre/42/individuel/brouillon/stocks',
    },
    {
      props: {
        offerId: '42',
        mode: OFFER_WIZARD_MODE.DRAFT,
        step: OFFER_WIZARD_STEP_IDS.SUMMARY,
        isV2: true,
      },
      expectedUrl: '/offre/42/individuel/brouillon/recapitulatif',
    },
    {
      props: {
        offerId: '42',
        mode: OFFER_WIZARD_MODE.DRAFT,
        step: OFFER_WIZARD_STEP_IDS.CONFIRMATION,
        isV2: true,
      },
      expectedUrl: '/offre/42/individuel/brouillon/confirmation',
    },
    // when edition mode
    {
      props: {
        offerId: '42',
        mode: OFFER_WIZARD_MODE.EDITION,
        step: OFFER_WIZARD_STEP_IDS.INFORMATIONS,
        isV2: true,
      },
      expectedUrl: '/offre/42/individuel/edition',
    },
    {
      props: {
        offerId: '42',
        mode: OFFER_WIZARD_MODE.EDITION,
        step: OFFER_WIZARD_STEP_IDS.STOCKS,
        isV2: true,
      },
      expectedUrl: '/offre/42/individuel/stocks',
    },
    {
      props: {
        offerId: '42',
        mode: OFFER_WIZARD_MODE.EDITION,
        step: OFFER_WIZARD_STEP_IDS.SUMMARY,
        isV2: true,
      },
      expectedUrl: '/offre/42/individuel/recapitulatif',
    },
    {
      props: {
        offerId: '42',
        mode: OFFER_WIZARD_MODE.EDITION,
        step: OFFER_WIZARD_STEP_IDS.CONFIRMATION,
        isV2: true,
      },
      expectedUrl: '',
    },
  ]
  it.each(propsAndExpectedV2)(
    'should return right v2 url',
    propsAndExpectedV2 => {
      const url = getOfferIndividualUrl(propsAndExpectedV2.props)

      expect(url).toBe(propsAndExpectedV2.expectedUrl)
    }
  )
})
