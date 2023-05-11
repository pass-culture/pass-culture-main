import { OFFER_WIZARD_STEP_IDS } from 'components/OfferIndividualBreadcrumb'
import { OFFER_WIZARD_MODE } from 'core/Offers'

import { computeNextStep } from '../computeNextStep'

describe('computeNextStep', () => {
  const testData = [
    {
      mode: OFFER_WIZARD_MODE.EDITION,
      isSubmittingDraft: true,
      isEvent: true,
      expected: OFFER_WIZARD_STEP_IDS.SUMMARY,
    },
    {
      mode: OFFER_WIZARD_MODE.DRAFT,
      isSubmittingDraft: true,
      isEvent: true,
      expected: OFFER_WIZARD_STEP_IDS.INFORMATIONS,
    },
    {
      mode: OFFER_WIZARD_MODE.DRAFT,
      isSubmittingDraft: true,
      isEvent: false,
      expected: OFFER_WIZARD_STEP_IDS.INFORMATIONS,
    },
    {
      mode: OFFER_WIZARD_MODE.CREATION,
      isSubmittingDraft: false,
      isEvent: true,
      expected: OFFER_WIZARD_STEP_IDS.TARIFS,
    },
    {
      mode: OFFER_WIZARD_MODE.CREATION,
      isSubmittingDraft: false,
      isEvent: false,
      expected: OFFER_WIZARD_STEP_IDS.STOCKS,
    },
  ]
  it.each(testData)(
    'should return right path',
    ({ mode, isSubmittingDraft, isEvent, expected }) => {
      const result = computeNextStep(mode, isSubmittingDraft, isEvent)

      expect(result).toBe(expected)
    }
  )
})
