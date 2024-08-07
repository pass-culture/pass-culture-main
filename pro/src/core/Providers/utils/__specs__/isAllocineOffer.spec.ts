import { getIndividualOfferFactory } from 'utils/individualApiFactories'

import { isAllocineOffer } from '../localProvider'

describe('isAllocineOffer', () => {
  it('should return true if last provider name is Allociné', () => {
    expect(
      isAllocineOffer(
        getIndividualOfferFactory({
          lastProvider: {
            name: 'Allociné',
          },
        })
      )
    ).toBe(true)
  })

  it('should return false if last provider name does not contain Allociné', () => {
    expect(
      isAllocineOffer(
        getIndividualOfferFactory({
          lastProvider: {
            name: 'Anyotherprovider',
          },
        })
      )
    ).toBe(false)
  })

  it('should return false if last provider is null', () => {
    expect(
      isAllocineOffer(
        getIndividualOfferFactory({
          lastProvider: null,
        })
      )
    ).toBe(false)
  })

  it('should return false if last provider is undefined', () => {
    expect(
      isAllocineOffer(getIndividualOfferFactory({ lastProvider: undefined }))
    ).toBe(false)
  })
})
