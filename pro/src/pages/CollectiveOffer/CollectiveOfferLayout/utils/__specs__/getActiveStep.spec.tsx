import { CollectiveOfferStep } from '../../CollectiveOfferNavigation/constants'
import {
  getCollectiveOfferActiveStep,
  getCollectiveOfferTemplateActiveStep,
} from '../getActiveStep'

describe('getCollectiveOfferActiveStep', () => {
  it('getCollectiveOfferActiveStep', () => {
    expect(getCollectiveOfferActiveStep('/blablabla/stocks')).toBe(
      CollectiveOfferStep.STOCKS
    )
    expect(getCollectiveOfferActiveStep('/blablabla/etablissement')).toBe(
      CollectiveOfferStep.INSTITUTION
    )
    expect(getCollectiveOfferActiveStep('/blablabla/recapitulatif')).toBe(
      CollectiveOfferStep.SUMMARY
    )
    expect(getCollectiveOfferActiveStep('/blablabla/apercu')).toBe(
      CollectiveOfferStep.PREVIEW
    )
    expect(getCollectiveOfferActiveStep('/blablabla')).toBe(
      CollectiveOfferStep.DETAILS
    )
  })
})

describe('getCollectiveOfferTemplateActiveStep', () => {
  it('getCollectiveOfferTemplateActiveStep', () => {
    expect(
      getCollectiveOfferTemplateActiveStep('/blablabla/recapitulatif')
    ).toBe(CollectiveOfferStep.SUMMARY)
    expect(getCollectiveOfferTemplateActiveStep('/blablabla/apercu')).toBe(
      CollectiveOfferStep.PREVIEW
    )
    expect(getCollectiveOfferTemplateActiveStep('/blablabla')).toBe(
      CollectiveOfferStep.DETAILS
    )
  })
})
