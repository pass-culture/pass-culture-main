import { selectOfferByRouterMatch } from '../offersSelector'

describe('selectOfferByRouterMatch', () => {
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
    const result = selectOfferByRouterMatch(state, match)

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
    const result = selectOfferByRouterMatch(state, match)

    // then
    expect(result).toStrictEqual({ id: 'AE' })
  })
})
