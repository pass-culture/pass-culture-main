import { OFFER_WIZARD_STEP_IDS } from 'components/OfferIndividualBreadcrumb'
import { OFFER_WIZARD_MODE } from 'core/Offers'

import { computeNextStep } from '../computeNextStep'

describe('computeNextStep', () => {
  const testData = [
    {
      mode: OFFER_WIZARD_MODE.EDITION,
      isSubmittingDraft: true,
      isEvent: true,
      isPriceCategoriesActive: true,
      expected: OFFER_WIZARD_STEP_IDS.SUMMARY,
    },
    {
      mode: OFFER_WIZARD_MODE.DRAFT,
      isSubmittingDraft: true,
      isEvent: true,
      isPriceCategoriesActive: true,
      expected: OFFER_WIZARD_STEP_IDS.INFORMATIONS,
    },
    {
      mode: OFFER_WIZARD_MODE.DRAFT,
      isSubmittingDraft: true,
      isEvent: false,
      isPriceCategoriesActive: true,
      expected: OFFER_WIZARD_STEP_IDS.INFORMATIONS,
    },
    {
      mode: OFFER_WIZARD_MODE.CREATION,
      isSubmittingDraft: false,
      isEvent: true,
      isPriceCategoriesActive: true,
      expected: OFFER_WIZARD_STEP_IDS.TARIFS,
    },
    {
      mode: OFFER_WIZARD_MODE.CREATION,
      isSubmittingDraft: false,
      isEvent: true,
      isPriceCategoriesActive: false,
      expected: OFFER_WIZARD_STEP_IDS.STOCKS,
    },
    {
      mode: OFFER_WIZARD_MODE.CREATION,
      isSubmittingDraft: false,
      isEvent: false,
      isPriceCategoriesActive: true,
      expected: OFFER_WIZARD_STEP_IDS.STOCKS,
    },
  ]
  it.each(testData)(
    'should retrun right path',
    ({
      mode,
      isSubmittingDraft,
      isEvent,
      isPriceCategoriesActive,
      expected,
    }) => {
      const result = computeNextStep(
        mode,
        isSubmittingDraft,
        isEvent,
        isPriceCategoriesActive
      )

      expect(result).toBe(expected)
    }
  )
})
