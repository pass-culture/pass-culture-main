import { CollectiveOfferDisplayedStatus } from '@/apiClient/v1'

import { getCollectiveOfferLink } from '../getCollectiveOfferLink'

describe('getCollectiveOfferLink', () => {
  it('should return the recap link for non draft offers', () => {
    expect(
      getCollectiveOfferLink(12, CollectiveOfferDisplayedStatus.BOOKED)
    ).toBe('/offre/12/collectif/recapitulatif')
  })

  it('should return the edition link for non draft offers in edition mode', () => {
    expect(
      getCollectiveOfferLink(
        'T-12',
        CollectiveOfferDisplayedStatus.PUBLISHED,
        true
      )
    ).toBe('/offre/T-12/collectif/edition')
  })

  it('should return the creation link for draft offers', () => {
    expect(
      getCollectiveOfferLink(12, CollectiveOfferDisplayedStatus.DRAFT)
    ).toBe('/offre/collectif/12/creation')
  })
})
