import selectOfferByMatch from '../selectOfferByMatch'

describe('src | selectors | selectOfferByMatch', () => {
  it('should return offer when offerId in match', () => {
    // given
    const state = {
      data: {
        bookings: [],
        favorites: [],
        offers: [{ id: 'AE' }],
        recommendations: [],
      },
    }
    const match = {
      params: {
        offerId: 'AE',
      },
    }

    // when
    const result = selectOfferByMatch(state, match)

    // then
    expect(result).toStrictEqual({ id: 'AE' })
  })

  it('should return offer when bookingId in match resolves booking', () => {
    // given
    const state = {
      data: {
        bookings: [{ id: 'BF', stock: { offerId: 'AE' } }],
        favorites: [],
        offers: [{ id: 'AE' }],
        recommendations: [],
        stocks: [],
      },
    }
    const match = {
      params: {
        bookingId: 'BF',
        offerId: 'AE',
      },
    }

    // when
    const result = selectOfferByMatch(state, match)

    // then
    expect(result).toStrictEqual({ id: 'AE' })
  })
})
