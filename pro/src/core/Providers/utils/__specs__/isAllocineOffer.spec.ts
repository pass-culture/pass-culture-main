import { IOfferIndividual } from 'core/Offers/types'

import { isAllocineOffer } from '../localProvider'

describe('isAllocineOffer', () => {
  it('should return true if last provider name is Allociné', () => {
    expect(
      isAllocineOffer({
        lastProvider: {
          name: 'Allociné',
        },
      } as IOfferIndividual) // TODO should use factory pattern
    ).toBe(true)
  })

  it('should return false if last provider name does not contain Allociné', () => {
    expect(
      isAllocineOffer({
        lastProvider: {
          name: 'Anyotherprovider',
        },
      } as IOfferIndividual)
    ).toBe(false)
  })

  it('should return false if last provider is null', () => {
    expect(
      isAllocineOffer({
        lastProvider: null,
      } as IOfferIndividual)
    ).toBe(false)
  })

  it('should return false if last provider is undefined', () => {
    expect(isAllocineOffer({} as IOfferIndividual)).toBe(false)
  })
})
