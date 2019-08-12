import selectIsFinishedByRouterMatch from '../selectIsFinishedByRouterMatch'

describe('src | selectors | selectIsFinishedByRouterMatch', () => {
  let offer

  beforeEach(() => {
    offer = {
      id: 'AE',
      isFinished: false,
    }
  })

  it('should return false when offerId in match', () => {
    // given
    const state = {
      data: {
        bookings: [],
        favorites: [],
        mediations: [],
        offers: [offer],
        recommendations: [],
        stocks: [],
      },
    }
    const match = {
      params: {
        offerId: 'AE',
      },
    }

    // when
    const result = selectIsFinishedByRouterMatch(state, match)

    // then
    expect(result).toBe(false)
  })

  it('should return false when bookingId in match resolves booking', () => {
    // given
    const bookingId = 'BF'
    const booking = {
      id: bookingId,
      stock: { offerId: 'AE' },
      stockId: 'AA',
    }
    const state = {
      data: {
        bookings: [booking],
        favorites: [],
        mediations: [],
        offers: [offer],
        recommendations: [],
        stocks: [{ id: 'AA' }],
      },
    }
    const match = {
      params: {
        bookingId,
      },
    }

    // when
    const result = selectIsFinishedByRouterMatch(state, match)

    // then
    expect(result).toBe(false)
  })

  it('should return false when favoriteId in match resolves offer', () => {
    // given
    const favoriteId = 'BF'
    const favorite = { id: favoriteId, offerId: 'AE' }
    const state = {
      data: {
        bookings: [],
        favorites: [favorite],
        mediations: [],
        offers: [offer],
        recommendations: [],
        stocks: [],
      },
    }
    const match = {
      params: {
        favoriteId,
      },
    }

    // when
    const result = selectIsFinishedByRouterMatch(state, match)

    // then
    expect(result).toBe(false)
  })
})
