import { OfferStatus } from '@/apiClient/v1'
import { getIndividualOfferFactory } from '@/commons/utils/factories/individualApiFactories'

import { isOfferDisabled } from '../isOfferDisabled'

describe('isOfferDisabled', () => {
  const offerBase = getIndividualOfferFactory()

  it('should return true for REJECTED', () => {
    expect(
      isOfferDisabled({
        ...offerBase,
        status: OfferStatus.REJECTED,
      })
    ).toBe(true)
  })

  it('should return true for PENDING', () => {
    expect(
      isOfferDisabled({
        ...offerBase,
        status: OfferStatus.PENDING,
      })
    ).toBe(true)
  })

  it('should return false for ACTIVE', () => {
    expect(
      isOfferDisabled({
        ...offerBase,
        status: OfferStatus.ACTIVE,
      })
    ).toBe(false)
  })

  it('should return false for DRAFT', () => {
    expect(
      isOfferDisabled({
        ...offerBase,
        status: OfferStatus.DRAFT,
      })
    ).toBe(false)
  })
})
