import { GetIndividualOfferFactory } from 'utils/apiFactories'

import { isAllocineOffer } from '../localProvider'

describe('isAllocineOffer', () => {
  it('should return true if last provider name is Allociné', () => {
    expect(
      isAllocineOffer(
        GetIndividualOfferFactory({
          lastProvider: {
            name: 'Allociné',
          },
        })
      ) // TODO should use factory pattern
    ).toBe(true)
  })

  it('should return false if last provider name does not contain Allociné', () => {
    expect(
      isAllocineOffer(
        GetIndividualOfferFactory({
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
        GetIndividualOfferFactory({
          lastProvider: null,
        })
      )
    ).toBe(false)
  })

  it('should return false if last provider is undefined', () => {
    expect(
      isAllocineOffer(GetIndividualOfferFactory({ lastProvider: undefined }))
    ).toBe(false)
  })
})
