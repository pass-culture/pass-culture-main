import { CollectiveOfferNavigationStep } from 'components/CollectiveOfferNavigation'

import { getActiveStep } from '../getActiveStep'

describe('getActiveStep', () => {
  it('getActiveStep', () => {
    expect(getActiveStep('/blablabla/stocks')).toBe(
      CollectiveOfferNavigationStep.STOCKS
    )
    expect(getActiveStep('/blablabla/visibilite')).toBe(
      CollectiveOfferNavigationStep.VISIBILITY
    )
    expect(getActiveStep('/blablabla/recapitulatif')).toBe(
      CollectiveOfferNavigationStep.SUMMARY
    )
    expect(getActiveStep('/blablabla')).toBe(
      CollectiveOfferNavigationStep.DETAILS
    )
  })
})
