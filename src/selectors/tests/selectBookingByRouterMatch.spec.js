import selectBookingByRouterMatch from '../selectBookingByRouterMatch'

describe('src | selectors | selectBookingByRouterMatch', () => {
  it('should return booking when bookingId in match', () => {
    // given
    const bookingId = 'AE'
    const booking = { id: bookingId }
    const state = {
      data: {
        bookings: [booking],
        favorites: [],
        offers: [],
        recommendations: [],
      },
    }
    const match = {
      params: {
        bookingId,
      },
    }

    // when
    const result = selectBookingByRouterMatch(state, match)

    // then
    expect(result).toStrictEqual(booking)
  })

  it('should return booking when favoriteId in match resolves first matching booking', () => {
    // given
    const stockId = 'CG'
    const stock = { id: stockId }
    const bookingId = 'AE'
    const booking = { id: bookingId, stockId }
    const offerId = 'BF'
    const offer = { id: offerId, stocks: [stock] }
    const favoriteId = 'BF'
    const favorite = { id: favoriteId, offerId }
    const state = {
      data: {
        bookings: [booking],
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
    const result = selectBookingByRouterMatch(state, match)

    // then
    expect(result).toStrictEqual(booking)
  })

  it('should return booking when found recommendation in match resolves first matching booking', () => {
    // given
    const stockId = 'CG'
    const stock = { id: stockId }
    const bookingId = 'AE'
    const booking = { id: bookingId, stockId }
    const offerId = 'BF'
    const offer = { id: offerId, stocks: [stock] }
    const recommendationId = 'BF'
    const recommendation = { id: recommendationId, offerId }
    const state = {
      data: {
        bookings: [booking],
        favorites: [],
        offers: [offer],
        recommendations: [recommendation],
      },
    }
    const match = {
      params: {
        offerId,
      },
    }

    // when
    const result = selectBookingByRouterMatch(state, match)

    // then
    expect(result).toStrictEqual(booking)
  })
})
