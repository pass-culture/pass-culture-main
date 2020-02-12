import isTiteLiveOffer from '../isTiteLiveOffer'

describe('components | OfferEdition | isTiteLiveOffer', () => {
  it('should return true if last provider name contains titelive', () => {
    // given
    const offer = {
      id: 'AZER',
      lastProvider: {
        name: 'TiteLive Stock Manager',
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
