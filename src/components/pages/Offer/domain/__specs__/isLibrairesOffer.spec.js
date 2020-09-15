import { isLibrairesOffer } from '../localProvider'

describe('src | isLibrairesOffer', () => {
  it('should return true if last provider name contains libraires', () => {
    // given
    const offer = {
      id: 'AZER',
      lastProvider: {
        name: 'Leslibraires.fr',
      },
    }

    // when
    const isOfferLibrairesGenerated = isLibrairesOffer(offer)

    // then
    expect(isOfferLibrairesGenerated).toBe(true)
  })

  it('should return false if last provider name does not contain libraires', () => {
    // given
    const offer = {
      id: 'AZER',
      lastProvider: {
        name: 'Anyotherprovider',
      },
    }

    // when
    const isOfferLibrairesGenerated = isLibrairesOffer(offer)

    // then
    expect(isOfferLibrairesGenerated).toBe(false)
  })

  it('should return false if last provider is null', () => {
    // given
    const offer = {
      id: 'AZER',
      lastProvider: null,
    }

    // when
    const isOfferLibrairesGenerated = isLibrairesOffer(offer)

    // then
    expect(isOfferLibrairesGenerated).toBe(false)
  })

  it('should return false if last provider is undefined', () => {
    // given
    const offer = {
      id: 'AZER',
    }

    // when
    const isOfferLibrairesGenerated = isLibrairesOffer(offer)

    // then
    expect(isOfferLibrairesGenerated).toBe(false)
  })
})
