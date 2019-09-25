import checkIfOfferIsTiteLiveGenerated from '../checkIfOfferIsTiteLiveGenerated'

describe('src | components | pages | Offer | utils | checkIfOfferIsTiteLiveGenerated', () => {
  it('should return true if last provider name contains titelive', () => {
    // given
    const offer = {
      id: 'AZER',
      lastProvider: {
        name: 'TiteLive Stock Manager',
      },
    }

    // when
    const isOfferTiteLiveGenerated = checkIfOfferIsTiteLiveGenerated(offer)

    // then
    expect(isOfferTiteLiveGenerated).toBe(true)
  })

  it('should return false if last provider name contains openagenda', () => {
    // given
    const offer = {
      id: 'AZER',
      lastProvider: {
        name: 'OpenAgenda',
      },
    }

    // when
    const isOfferTiteLiveGenerated = checkIfOfferIsTiteLiveGenerated(offer)

    // then
    expect(isOfferTiteLiveGenerated).toBe(false)
  })
})
