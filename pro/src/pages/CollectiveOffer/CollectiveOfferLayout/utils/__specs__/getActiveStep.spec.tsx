import { CollectiveOfferStep } from '../../CollectiveOfferNavigation/constants'
import {
  getCollectiveOfferActiveStep,
  getCollectiveOfferTemplateActiveStep,
} from '../getActiveStep'

describe('getCollectiveOfferActiveStep', () => {
  it('should map the active step to a given url', () => {
    expect(getCollectiveOfferActiveStep('/blablabla/stocks')).toBe(
      CollectiveOfferStep.STOCKS
    )
    expect(
      getCollectiveOfferActiveStep('/blablabla/informations-pratiques')
    ).toBe(CollectiveOfferStep.INFORMATION)
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
  it('should map the active step to a given url', () => {
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
