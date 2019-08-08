import selectDistanceByRouterMatch from '../selectDistanceByRouterMatch'

describe('src | selectors | selectDistanceByRouterMatch', () => {
  let offer
  let offerId
  let expectedDistance = '56 km'
  beforeEach(() => {
    offerId = 'AE'
    offer = {
      id: offerId,
      venue: {
        latitude: 42,
        longitude: 1.6,
      },
    }
  })

  it('should return distance when offerId in match', () => {
    // given

    const state = {
      data: {
        bookings: [],
        favorites: [],
        mediations: [],
        offers: [offer],
        recommendations: [],
      },
      geolocation: {
        latitude: 42.5,
        longitude: 1.7,
      },
    }
    const match = {
      params: {
        offerId,
      },
    }

    // when
    const result = selectDistanceByRouterMatch(state, match)

    // then
    expect(result).toStrictEqual(expectedDistance)
  })

  it('should return offer when bookingId in match resolves booking', () => {
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
      geolocation: {
        latitude: 42.5,
        longitude: 1.7,
      },
    }
    const match = {
      params: {
        bookingId,
      },
    }

    // when
    const result = selectDistanceByRouterMatch(state, match)

    // then
    expect(result).toStrictEqual(expectedDistance)
  })

  it('should return distance when favoriteId in match resolves offer', () => {
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
      geolocation: {
        latitude: 42.5,
        longitude: 1.7,
      },
    }
    const match = {
      params: {
        favoriteId,
      },
    }

    // when
    const result = selectDistanceByRouterMatch(state, match)

    // then
    expect(result).toStrictEqual('-')
  })
})
