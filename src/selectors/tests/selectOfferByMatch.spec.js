import selectOfferByMatch from '../selectOfferByMatch'

describe('src | selectors | selectOfferByMatch', () => {
  it('should return offer when offerId in match', () => {
    // given
    const offerId = 'AE'
    const offer = { id: offerId }
    const state = {
      data: {
        bookings: [],
        favorites: [],
        offers: [offer],
        recommendations: [],
      },
    }
    const match = {
      params: {
        offerId,
      },
    }

    // when
    const result = selectOfferByMatch(state, match)

    // then
    expect(result).toStrictEqual(offer)
  })

  it('should return offer when bookingId in match resolves booking', () => {
    // given
    const offerId = 'AE'
    const offer = { id: offerId }
    const bookingId = 'BF'
    const booking = { id: bookingId, stock: { offerId } }
    const state = {
      data: {
        bookings: [booking],
        favorites: [],
        offers: [offer],
        recommendations: [],
      },
    }
    const match = {
      params: {
        bookingId,
      },
    }

    // when
    const result = selectOfferByMatch(state, match)

    // then
    expect(result).toStrictEqual(offer)
  })

  it('should return offer when favoriteId in match resolves offer', () => {
    // given
    const offerId = 'AE'
    const offer = { id: offerId }
    const favoriteId = 'BF'
    const favorite = { id: favoriteId, offerId }
    const state = {
      data: {
        bookings: [],
        favorites: [favorite],
        offers: [offer],
        recommendations: [],
      },
    }
    const match = {
      params: {
        favoriteId,
      },
    }

    // when
    const result = selectOfferByMatch(state, match)

    // then
    expect(result).toStrictEqual(offer)
  })
})
