import { OfferStatus } from 'apiClient/v1'
import { individualOfferForOffersListFactory } from 'screens/Offers/utils/individualOffersFactories'

import { canDeleteOffers } from '../canDeleteOffers'

describe('canDeleteOffers', () => {
  it('should return true if all offers are draft', () => {
    const offers = [
      individualOfferForOffersListFactory({ status: OfferStatus.DRAFT }),
      individualOfferForOffersListFactory({ status: OfferStatus.DRAFT }),
    ]
    const tmpSelectedOfferIds = [
      offers[0].id.toString(),
      offers[1].id.toString(),
    ]

    const result = canDeleteOffers(offers, tmpSelectedOfferIds)

    expect(result).toStrictEqual(true)
  })

  it('should return false if one offer is not draft', () => {
    const offers = [
      individualOfferForOffersListFactory({ status: OfferStatus.ACTIVE }),
      individualOfferForOffersListFactory({ status: OfferStatus.DRAFT }),
    ]
    const tmpSelectedOfferIds = [
      offers[0].id.toString(),
      offers[1].id.toString(),
    ]

    const result = canDeleteOffers(offers, tmpSelectedOfferIds)

    expect(result).toStrictEqual(false)
  })
})
