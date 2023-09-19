import { IndividualOffer } from 'core/Offers/types'

import { isAllocineOffer } from '../localProvider'

describe('isAllocineOffer', () => {
  it('should return true if last provider name is Allociné', () => {
    expect(
      isAllocineOffer({
        lastProvider: {
          name: 'Allociné',
        },
      } as IndividualOffer) // TODO should use factory pattern
    ).toBe(true)
  })

  it('should return false if last provider name does not contain Allociné', () => {
    expect(
      isAllocineOffer({
        lastProvider: {
          name: 'Anyotherprovider',
        },
      } as IndividualOffer)
    ).toBe(false)
  })

  it('should return false if last provider is null', () => {
    expect(
      isAllocineOffer({
        lastProvider: null,
      } as IndividualOffer)
    ).toBe(false)
  })

  it('should return false if last provider is undefined', () => {
    expect(isAllocineOffer({} as IndividualOffer)).toBe(false)
  })
})
