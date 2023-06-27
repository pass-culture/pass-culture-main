import { OfferIndividual } from 'core/Offers/types'

import { isAllocineOffer } from '../localProvider'

describe('isAllocineOffer', () => {
  it('should return true if last provider name is Allociné', () => {
    expect(
      isAllocineOffer({
        lastProvider: {
          name: 'Allociné',
        },
      } as OfferIndividual) // TODO should use factory pattern
    ).toBe(true)
  })

  it('should return false if last provider name does not contain Allociné', () => {
    expect(
      isAllocineOffer({
        lastProvider: {
          name: 'Anyotherprovider',
        },
      } as OfferIndividual)
    ).toBe(false)
  })

  it('should return false if last provider is null', () => {
    expect(
      isAllocineOffer({
        lastProvider: null,
      } as OfferIndividual)
    ).toBe(false)
  })

  it('should return false if last provider is undefined', () => {
    expect(isAllocineOffer({} as OfferIndividual)).toBe(false)
  })
})
