import selectIsFinishedByRouterMatch from '../selectIsFinishedByRouterMatch'

describe('src | selectors | selectIsFinishedByRouterMatch', () => {
  let offer
  let offerId
  let isFinished = false
  beforeEach(() => {
    offerId = 'AE'
    offer = {
      id: offerId,
      isFinished,
    }
  })

  it('should return isFinished when offerId in match', () => {
    // given

    const state = {
      data: {
        bookings: [],
        favorites: [],
        mediations: [],
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
    const result = selectIsFinishedByRouterMatch(state, match)

    // then
    expect(result).toStrictEqual(isFinished)
  })

  it('should return isFinished when bookingId in match resolves booking', () => {
    // given
    const bookingId = 'BF'
    const booking = { id: bookingId, stock: { offerId } }
    const state = {
      data: {
        bookings: [booking],
        favorites: [],
        mediations: [],
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
    const result = selectIsFinishedByRouterMatch(state, match)

    // then
    expect(result).toStrictEqual(isFinished)
  })

  it('should return isFinished when favoriteId in match resolves offer', () => {
    // given
    const favoriteId = 'BF'
    const favorite = { id: favoriteId, offerId }
    const state = {
      data: {
        bookings: [],
        favorites: [favorite],
        mediations: [],
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
    const result = selectIsFinishedByRouterMatch(state, match)

    // then
    expect(result).toStrictEqual(isFinished)
  })
})
