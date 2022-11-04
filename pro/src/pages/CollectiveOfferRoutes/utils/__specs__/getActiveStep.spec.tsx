import { OfferBreadcrumbStep } from 'new_components/OfferBreadcrumb'

import { getActiveStep } from '../getActiveStep'

describe('getActiveStep', () => {
  it('getActiveStep', () => {
    expect(getActiveStep('/blablabla/stocks')).toBe(OfferBreadcrumbStep.STOCKS)
    expect(getActiveStep('/blablabla/visibilite')).toBe(
      OfferBreadcrumbStep.VISIBILITY
    )
    expect(getActiveStep('/blablabla/recapitulatif')).toBe(
      OfferBreadcrumbStep.SUMMARY
    )
    expect(getActiveStep('/blablabla')).toBe(OfferBreadcrumbStep.DETAILS)
  })
})
