import { getIndividualOfferFactory } from '@/commons/utils/factories/individualApiFactories'

import { isOfferSynchronized } from '../isOfferSynchronized'

describe('isOfferSynchronized', () => {
  it('should return true when lastProvider exists', () => {
    const offer = getIndividualOfferFactory({
      lastProvider: { name: 'SomeProvider' },
    })

    expect(isOfferSynchronized(offer)).toBe(true)
  })

  it('should return false when lastProvider is null', () => {
    const offer = getIndividualOfferFactory({
      // TODO (tpommellet) to remove once GetIndividualOfferWithAddressResponseModel is migrated to Pydantic V2
      // @ts-expect-error
      lastProvider: null,
    })

    expect(isOfferSynchronized(offer)).toBe(false)
  })

  it('should return false when lastProvider is ommitted', () => {
    const offer = getIndividualOfferFactory()

    expect(isOfferSynchronized(offer)).toBe(false)
  })
})
