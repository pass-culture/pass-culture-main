import isAllocineOffer from '../isAllocineOffer'

describe('src | components | pages | Offer | utils | isAllocineOffer', () => {
  it('should return true if last provider name is Allociné', () => {
    // given
    const offer = {
      id: 'AZER',
      lastProvider: {
        name: 'Allociné',
      },
    }

    // when
    const isOfferAllocineGenerated = isAllocineOffer(offer)

    // then
    expect(isOfferAllocineGenerated).toBe(true)
  })

  it('should return false if last provider name does not contain Allociné', () => {
    // given
    const offer = {
      id: 'AZER',
      lastProvider: {
        name: 'Anyotherprovider',
      },
    }

    // when
    const isOfferAllocineGenerated = isAllocineOffer(offer)

    // then
    expect(isOfferAllocineGenerated).toBe(false)
  })
})
