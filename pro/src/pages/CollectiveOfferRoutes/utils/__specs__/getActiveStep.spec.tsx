import { CollectiveOfferStep } from '@/pages/CollectiveOffer/CollectiveOfferLayout/CollectiveOfferNavigation/CollectiveCreationOfferNavigation'

import { getActiveStep } from '../getActiveStep'

describe('getActiveStep', () => {
  it('getActiveStep', () => {
    expect(getActiveStep('/blablabla/stocks')).toBe(CollectiveOfferStep.STOCKS)
    expect(getActiveStep('/blablabla/etablissement')).toBe(
      CollectiveOfferStep.INSTITUTION
    )
    expect(getActiveStep('/blablabla/recapitulatif')).toBe(
      CollectiveOfferStep.SUMMARY
    )
    expect(getActiveStep('/blablabla')).toBe(CollectiveOfferStep.DETAILS)
  })
})
