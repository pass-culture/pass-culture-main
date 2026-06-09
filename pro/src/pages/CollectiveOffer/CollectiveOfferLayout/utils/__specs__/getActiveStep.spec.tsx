import { CollectiveOfferStep } from '../../CollectiveOfferNavigation/CollectiveOfferCreationNavigation'
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
    expect(getActiveStep('/blablabla/apercu')).toBe(CollectiveOfferStep.PREVIEW)

    expect(getActiveStep('/blablabla')).toBe(CollectiveOfferStep.DETAILS)
  })
})
