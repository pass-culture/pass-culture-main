import moment from 'moment'

import selectBookingByRouterMatch from '../selectBookingByRouterMatch'

describe('src | selectors | selectBookingByRouterMatch', () => {
  it('should return booking when bookingId in match', () => {
    // given
    const state = {
      data: {
        bookings: [{ id: 'AE' }],
        offers: [],
        stocks: [],
      },
    }
    const match = {
      params: {
        bookingId: 'AE',
      },
    }

    // when
    const result = selectBookingByRouterMatch(state, match)

    // then
    expect(result).toStrictEqual({ id: 'AE' })
  })

  it('should return booking when found offer in match resolves first matching booking', () => {
    // given
    const now = moment()
    const twoDaysAfterNow = now.add(2, 'days').format()
    const state = {
      data: {
        bookings: [{ id: 'AE', stockId: 'CG' }],
        offers: [{ id: 'BF' }],
        stocks: [{ id: 'CG', offerId: 'BF', beginningDatetime: twoDaysAfterNow }],
      },
    }
    const match = {
      params: {
        offerId: 'BF',
      },
    }

    // when
    const result = selectBookingByRouterMatch(state, match)

    // then
    expect(result).toStrictEqual({ id: 'AE', stockId: 'CG' })
  })
})
