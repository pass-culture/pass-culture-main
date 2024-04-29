import { CollectiveOfferStep } from 'components/CollectiveOfferNavigation/CollectiveOfferNavigation'

import { getActiveStep } from '../getActiveStep'

describe('getActiveStep', () => {
  it('getActiveStep', () => {
    expect(getActiveStep('/blablabla/stocks')).toBe(CollectiveOfferStep.STOCKS)
    expect(getActiveStep('/blablabla/visibilite')).toBe(
      CollectiveOfferStep.VISIBILITY
    )
    expect(getActiveStep('/blablabla/recapitulatif')).toBe(
      CollectiveOfferStep.SUMMARY
    )
    expect(getActiveStep('/blablabla')).toBe(CollectiveOfferStep.DETAILS)
  })
})
