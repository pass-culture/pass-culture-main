import isLibrairesOffer from '../isLibrairesOffer'

describe('src | components | pages | Offer | utils | isLibrairesOffer', () => {
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

  it('should return false if last provider name is "TiteLive Stocks (Epagine / Place des libraires.com)"', () => {
    // given
    const offer = {
      id: 'AZER',
      lastProvider: {
        name: 'TiteLive Stocks (Epagine / Place des libraires.com)',
      },
    }

    // when
    const isOfferLibrairesGenerated = isLibrairesOffer(offer)

    // then
    expect(isOfferLibrairesGenerated).toBe(false)
  })
})
