import { selectOfferById, selectOfferByRouterMatch } from '../offersSelectors'

describe('selectOfferById', () => {
  it('should return undefined when no match', () => {
    // given
    const state = {
      data: {
        offers: [{ id: 'AE' }],
      },
    }

    // when
    const result = selectOfferById(state, 'wrong')

    // then
    expect(result).toBeUndefined()
  })

  it('should return offer matching id', () => {
    // given
    const state = {
      data: {
        offers: [{ id: 'foo' }, { id: 'bar' }, { id: 'baz' }],
      },
    }

    // when
    const result = selectOfferById(state, 'bar')

    // then
    expect(result).toStrictEqual({ id: 'bar' })
    expect(result).toBe(state.data.offers[1])
  })
})

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
        bookings: [{ id: 'BF', stockId: 'BE' }],
        favorites: [],
        offers: [{ id: 'AE' }],
        recommendations: [],
        stocks: [{ id: 'BE', offerId: 'AE' }],
      },
    }
    const match = {
      params: {
        bookingId: 'BF',
      },
    }

    // when
    const result = selectOfferByRouterMatch(state, match)

    // then
    expect(result).toStrictEqual({ id: 'AE' })
  })
})
