import { OFFER_WIZARD_STEP_IDS } from 'components/OfferIndividualBreadcrumb'
import { OFFER_WIZARD_MODE } from 'core/Offers'

import getOfferIndividualUrl from '../getOfferIndividualUrl'

describe('getOfferIndividualUrl', () => {
  const offerId = 42
  const propsAndExpectedV3 = [
    // when no offer (mode is no relevant)
    {
      props: {
        offerId: undefined,
        mode: OFFER_WIZARD_MODE.CREATION,
        step: OFFER_WIZARD_STEP_IDS.INFORMATIONS,
        isV2: false,
      },
      expectedUrl: '/offre/individuelle/creation/informations',
    },
    // when creation mode
    {
      props: {
        offerId: offerId,
        mode: OFFER_WIZARD_MODE.CREATION,
        step: OFFER_WIZARD_STEP_IDS.INFORMATIONS,
        isV2: false,
      },
      expectedUrl: '/offre/individuelle/42/creation/informations',
    },
    {
      props: {
        offerId: offerId,
        mode: OFFER_WIZARD_MODE.CREATION,
        step: OFFER_WIZARD_STEP_IDS.STOCKS,
        isV2: false,
      },
      expectedUrl: '/offre/individuelle/42/creation/stocks',
    },
    {
      props: {
        offerId: offerId,
        mode: OFFER_WIZARD_MODE.CREATION,
        step: OFFER_WIZARD_STEP_IDS.SUMMARY,
        isV2: false,
      },
      expectedUrl: '/offre/individuelle/42/creation/recapitulatif',
    },
    {
      props: {
        offerId: offerId,
        mode: OFFER_WIZARD_MODE.CREATION,
        step: OFFER_WIZARD_STEP_IDS.CONFIRMATION,
        isV2: false,
      },
      expectedUrl: '/offre/individuelle/42/creation/confirmation',
    },
    {
      props: {
        offerId: offerId,
        mode: OFFER_WIZARD_MODE.CREATION,
        step: OFFER_WIZARD_STEP_IDS.TARIFS,
        isV2: false,
      },
      expectedUrl: '/offre/individuelle/42/creation/tarifs',
    },
    // when brouillon mode
    {
      props: {
        offerId: offerId,
        mode: OFFER_WIZARD_MODE.DRAFT,
        step: OFFER_WIZARD_STEP_IDS.INFORMATIONS,
        isV2: false,
      },
      expectedUrl: '/offre/individuelle/42/brouillon/informations',
    },
    {
      props: {
        offerId: offerId,
        mode: OFFER_WIZARD_MODE.DRAFT,
        step: OFFER_WIZARD_STEP_IDS.STOCKS,
        isV2: false,
      },
      expectedUrl: '/offre/individuelle/42/brouillon/stocks',
    },
    {
      props: {
        offerId: offerId,
        mode: OFFER_WIZARD_MODE.DRAFT,
        step: OFFER_WIZARD_STEP_IDS.SUMMARY,
        isV2: false,
      },
      expectedUrl: '/offre/individuelle/42/brouillon/recapitulatif',
    },
    {
      props: {
        offerId: offerId,
        mode: OFFER_WIZARD_MODE.DRAFT,
        step: OFFER_WIZARD_STEP_IDS.CONFIRMATION,
        isV2: false,
      },
      expectedUrl: '/offre/individuelle/42/brouillon/confirmation',
    },

    {
      props: {
        offerId: offerId,
        mode: OFFER_WIZARD_MODE.DRAFT,
        step: OFFER_WIZARD_STEP_IDS.TARIFS,
        isV2: false,
      },
      expectedUrl: '/offre/individuelle/42/brouillon/tarifs',
    },
    // when edition mode
    {
      props: {
        offerId: offerId,
        mode: OFFER_WIZARD_MODE.EDITION,
        step: OFFER_WIZARD_STEP_IDS.INFORMATIONS,
        isV2: false,
      },
      expectedUrl: '/offre/individuelle/42/informations',
    },
    {
      props: {
        offerId: offerId,
        mode: OFFER_WIZARD_MODE.EDITION,
        step: OFFER_WIZARD_STEP_IDS.STOCKS,
        isV2: false,
      },
      expectedUrl: '/offre/individuelle/42/stocks',
    },
    {
      props: {
        offerId: offerId,
        mode: OFFER_WIZARD_MODE.EDITION,
        step: OFFER_WIZARD_STEP_IDS.SUMMARY,
        isV2: false,
      },
      expectedUrl: '/offre/individuelle/42/recapitulatif',
    },
    {
      props: {
        offerId: offerId,
        mode: OFFER_WIZARD_MODE.EDITION,
        step: OFFER_WIZARD_STEP_IDS.CONFIRMATION,
        isV2: false,
      },
      expectedUrl: '',
    },
    {
      props: {
        offerId: offerId,
        mode: OFFER_WIZARD_MODE.EDITION,
        step: OFFER_WIZARD_STEP_IDS.TARIFS,
        isV2: false,
      },
      expectedUrl: '/offre/individuelle/42/tarifs',
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
        offerId: offerId,
        mode: OFFER_WIZARD_MODE.CREATION,
        step: OFFER_WIZARD_STEP_IDS.INFORMATIONS,
        isV2: true,
      },
      expectedUrl: '/offre/42/individuel/creation',
    },
    {
      props: {
        offerId: offerId,
        mode: OFFER_WIZARD_MODE.CREATION,
        step: OFFER_WIZARD_STEP_IDS.STOCKS,
        isV2: true,
      },
      expectedUrl: '/offre/42/individuel/creation/stocks',
    },
    {
      props: {
        offerId: offerId,
        mode: OFFER_WIZARD_MODE.CREATION,
        step: OFFER_WIZARD_STEP_IDS.SUMMARY,
        isV2: true,
      },
      expectedUrl: '/offre/42/individuel/creation/recapitulatif',
    },
    {
      props: {
        offerId: offerId,
        mode: OFFER_WIZARD_MODE.CREATION,
        step: OFFER_WIZARD_STEP_IDS.CONFIRMATION,
        isV2: true,
      },
      expectedUrl: '/offre/42/individuel/creation/confirmation',
    },
    {
      props: {
        offerId: offerId,
        mode: OFFER_WIZARD_MODE.CREATION,
        step: OFFER_WIZARD_STEP_IDS.TARIFS,
        isV2: true,
      },
      expectedUrl: '/offre/42/individuel/creation/tarifs',
    },
    // when brouillon mode
    {
      props: {
        offerId: offerId,
        mode: OFFER_WIZARD_MODE.DRAFT,
        step: OFFER_WIZARD_STEP_IDS.INFORMATIONS,
        isV2: true,
      },
      expectedUrl: '/offre/42/individuel/brouillon',
    },
    {
      props: {
        offerId: offerId,
        mode: OFFER_WIZARD_MODE.DRAFT,
        step: OFFER_WIZARD_STEP_IDS.STOCKS,
        isV2: true,
      },
      expectedUrl: '/offre/42/individuel/brouillon/stocks',
    },
    {
      props: {
        offerId: offerId,
        mode: OFFER_WIZARD_MODE.DRAFT,
        step: OFFER_WIZARD_STEP_IDS.SUMMARY,
        isV2: true,
      },
      expectedUrl: '/offre/42/individuel/brouillon/recapitulatif',
    },
    {
      props: {
        offerId: offerId,
        mode: OFFER_WIZARD_MODE.DRAFT,
        step: OFFER_WIZARD_STEP_IDS.CONFIRMATION,
        isV2: true,
      },
      expectedUrl: '/offre/42/individuel/brouillon/confirmation',
    },
    {
      props: {
        offerId: offerId,
        mode: OFFER_WIZARD_MODE.DRAFT,
        step: OFFER_WIZARD_STEP_IDS.TARIFS,
        isV2: true,
      },
      expectedUrl: '/offre/42/individuel/brouillon/tarifs',
    },
    // when edition mode
    {
      props: {
        offerId: offerId,
        mode: OFFER_WIZARD_MODE.EDITION,
        step: OFFER_WIZARD_STEP_IDS.INFORMATIONS,
        isV2: true,
      },
      expectedUrl: '/offre/42/individuel/edition',
    },
    {
      props: {
        offerId: offerId,
        mode: OFFER_WIZARD_MODE.EDITION,
        step: OFFER_WIZARD_STEP_IDS.STOCKS,
        isV2: true,
      },
      expectedUrl: '/offre/42/individuel/stocks',
    },
    {
      props: {
        offerId: offerId,
        mode: OFFER_WIZARD_MODE.EDITION,
        step: OFFER_WIZARD_STEP_IDS.SUMMARY,
        isV2: true,
      },
      expectedUrl: '/offre/42/individuel/recapitulatif',
    },
    {
      props: {
        offerId: offerId,
        mode: OFFER_WIZARD_MODE.EDITION,
        step: OFFER_WIZARD_STEP_IDS.CONFIRMATION,
        isV2: true,
      },
      expectedUrl: '',
    },

    {
      props: {
        offerId: offerId,
        mode: OFFER_WIZARD_MODE.EDITION,
        step: OFFER_WIZARD_STEP_IDS.TARIFS,
        isV2: true,
      },
      expectedUrl: '/offre/42/individuel/tarifs',
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
