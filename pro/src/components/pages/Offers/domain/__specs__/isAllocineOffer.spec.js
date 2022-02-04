import { isAllocineOffer } from '../localProvider'

describe('src | isAllocineOffer', () => {
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

  it('should return false if last provider is null', () => {
    // given
    const offer = {
      id: 'AZER',
      lastProvider: null,
    }

    // when
    const isOfferLibrairesGenerated = isAllocineOffer(offer)

    // then
    expect(isOfferLibrairesGenerated).toBe(false)
  })

  it('should return false if last provider is undefined', () => {
    // given
    const offer = {
      id: 'AZER',
    }

    // when
    const isOfferLibrairesGenerated = isAllocineOffer(offer)

    // then
    expect(isOfferLibrairesGenerated).toBe(false)
  })
})
