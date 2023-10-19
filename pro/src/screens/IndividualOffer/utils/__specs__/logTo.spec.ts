import { OFFER_WIZARD_STEP_IDS } from 'components/IndividualOfferBreadcrumb/constants'

import { logTo } from '../logTo'

describe('logTo', () => {
  const nextLocation = [
    OFFER_WIZARD_STEP_IDS.INFORMATIONS,
    OFFER_WIZARD_STEP_IDS.TARIFS,
    OFFER_WIZARD_STEP_IDS.STOCKS,
    OFFER_WIZARD_STEP_IDS.SUMMARY,
    'otherLocation',
  ]
  it.each(nextLocation)('should log %s right location', (location) => {
    const result = logTo(location)

    expect(result).toBe(location)
  })
})
