import { CollectiveOfferBreadcrumbStep } from 'components/CollectiveOfferBreadcrumb'

import { getActiveStep } from '../getActiveStep'

describe('getActiveStep', () => {
  it('getActiveStep', () => {
    expect(getActiveStep('/blablabla/stocks')).toBe(
      CollectiveOfferBreadcrumbStep.STOCKS
    )
    expect(getActiveStep('/blablabla/visibilite')).toBe(
      CollectiveOfferBreadcrumbStep.VISIBILITY
    )
    expect(getActiveStep('/blablabla/recapitulatif')).toBe(
      CollectiveOfferBreadcrumbStep.SUMMARY
    )
    expect(getActiveStep('/blablabla')).toBe(
      CollectiveOfferBreadcrumbStep.DETAILS
    )
  })
})
