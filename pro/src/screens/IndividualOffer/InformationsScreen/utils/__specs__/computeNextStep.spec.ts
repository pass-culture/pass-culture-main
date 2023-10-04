import { OFFER_WIZARD_STEP_IDS } from 'components/IndividualOfferBreadcrumb/constants'
import { OFFER_WIZARD_MODE } from 'core/Offers/constants'

import { computeNextStep } from '../computeNextStep'

describe('computeNextStep', () => {
  const testData = [
    {
      mode: OFFER_WIZARD_MODE.CREATION,
      isEvent: true,
      expected: OFFER_WIZARD_STEP_IDS.TARIFS,
    },
    {
      mode: OFFER_WIZARD_MODE.CREATION,
      isEvent: false,
      expected: OFFER_WIZARD_STEP_IDS.STOCKS,
    },
  ]
  it.each(testData)(
    'should return right path',
    ({ mode, isEvent, expected }) => {
      const result = computeNextStep(mode, isEvent)

      expect(result).toBe(expected)
    }
  )
})
