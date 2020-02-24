import isTiteLiveOffer from '../isTiteLiveOffer'

describe('src | components | pages | Offer | utils | isTiteLiveOffer', () => {
  it('should return true if last provider name contains titelive', () => {
    // given
    const offer = {
      id: 'AZER',
      lastProvider: {
        name: 'TiteLive Stocks (Epagine / Place des libraires.com)',
      },
    }

    // when
    const isOfferTiteLiveGenerated = isTiteLiveOffer(offer)

    // then
    expect(isOfferTiteLiveGenerated).toBe(true)
  })

  it('should return false if last provider name contains Open Agenda', () => {
    // given
    const offer = {
      id: 'AZER',
      lastProvider: {
        name: 'OpenAgenda',
      },
    }

    // when
    const isOfferTiteLiveGenerated = isTiteLiveOffer(offer)

    // then
    expect(isOfferTiteLiveGenerated).toBe(false)
  })
})
