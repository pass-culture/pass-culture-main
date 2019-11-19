import moment from 'moment'

import {
  selectBookingById,
  selectBookingByRouterMatch,
  selectBookingsOfTheWeek,
  selectBookingsOrderedByBeginningDateTimeAsc,
  selectCancelledBookings,
  selectFinishedBookings,
  selectFirstMatchingBookingByOfferId,
  selectUpComingBookings,
  selectUsedBookings,
} from '../bookingsSelectors'

describe('selectBookingsOfTheWeek()', () => {
  it('should return bookings of the week', () => {
    // given
    jest.spyOn(Date, 'now').mockImplementation(() => '2000-01-01T20:00:00Z')
    const oneDayBeforeNow = new Date('1999-12-31T20:00:00.00Z').toISOString()
    const fourDaysAfterNow = new Date('2000-01-04T20:00:00.00Z').toISOString()
    const fourDaysAfterNowBis = new Date('2000-01-04T10:00:00.00Z').toISOString()
    const nineDaysAfterNow = new Date('2000-01-09T20:00:00.01Z').toISOString()
    const permanent = null
    const state = {
      data: {
        bookings: [
          {
            id: 'b1',
            isCancelled: false,
            isUsed: false,
            stockId: 's1',
          },
          {
            id: 'b2',
            isCancelled: false,
            isUsed: false,
            stockId: 's2',
          },
          {
            id: 'b3',
            isCancelled: false,
            isUsed: false,
            stockId: 's3',
          },
          {
            id: 'b4',
            isCancelled: false,
            isUsed: false,
            stockId: 's4',
          },
          {
            id: 'b5',
            isCancelled: true,
            isUsed: false,
            stockId: 's5',
          },
          {
            id: 'b6',
            isCancelled: false,
            isUsed: true,
            stockId: 's6',
          },
          {
            id: 'b7',
            isCancelled: false,
            isUsed: false,
            stockId: 's7',
          },
        ],
        offers: [
          {
            id: 'o1',
            venue: {
              departementCode: '97',
            },
          },
          {
            id: 'o2',
            venue: {
              departementCode: '97',
            },
          },
          {
            id: 'o3',
            venue: {
              departementCode: '97',
            },
          },
          {
            id: 'o4',
            venue: {
              departementCode: '97',
            },
          },
          {
            id: 'o5',
            venue: {
              departementCode: '97',
            },
          },
          {
            id: 'o6',
            venue: {
              departementCode: '97',
            },
          },
          {
            id: 'o7',
            venue: {
              departementCode: '97',
            },
          },
        ],
        stocks: [
          {
            beginningDatetime: oneDayBeforeNow,
            id: 's1',
            offerId: 'o1',
          },
          {
            beginningDatetime: fourDaysAfterNow,
            id: 's2',
            offerId: 'o2',
          },
          {
            beginningDatetime: nineDaysAfterNow,
            id: 's3',
            offerId: 'o3',
          },
          {
            beginningDatetime: permanent,
            id: 's4',
            offerId: 'o4',
          },
          {
            beginningDatetime: fourDaysAfterNow,
            id: 's5',
            offerId: 'o5',
          },
          {
            beginningDatetime: fourDaysAfterNow,
            id: 's6',
            offerId: 'o6',
          },
          {
            beginningDatetime: fourDaysAfterNowBis,
            id: 's7',
            offerId: 'o7',
          },
        ],
      },
    }

    // when
    const results = selectBookingsOfTheWeek(state)

    // then
    expect(results).toStrictEqual([
      {
        id: 'b7',
        isCancelled: false,
        isUsed: false,
        stockId: 's7',
      },
      {
        id: 'b2',
        isCancelled: false,
        isUsed: false,
        stockId: 's2',
      },
    ])
  })
})

describe('selectUpComingBookings()', () => {
  it('should return up coming bookings', () => {
    // given
    jest.spyOn(Date, 'now').mockImplementation(() => '2000-01-01T20:00:00Z')
    const oneDayBeforeNow = new Date('1999-12-31T20:00:00.00Z').toISOString()
    const fourDaysAfterNow = new Date('2000-01-04T20:00:00.00Z').toISOString()
    const nineDaysAfterNow = new Date('2000-01-09T20:00:00.01Z').toISOString()
    const permanent = null
    const state = {
      data: {
        bookings: [
          {
            id: 'b1',
            isCancelled: false,
            isUsed: false,
            stockId: 's1',
          },
          {
            id: 'b2',
            isCancelled: false,
            isUsed: false,
            stockId: 's2',
          },
          {
            id: 'b3',
            isCancelled: false,
            isUsed: false,
            stockId: 's3',
          },
          {
            id: 'b4',
            isCancelled: false,
            isUsed: false,
            stockId: 's4',
          },
          {
            id: 'b5',
            isCancelled: true,
            isUsed: false,
            stockId: 's5',
          },
          {
            id: 'b6',
            isCancelled: false,
            isUsed: true,
            stockId: 's6',
          },
        ],
        offers: [
          {
            id: 'o1',
            venue: {
              departementCode: '97',
            },
          },
          {
            id: 'o2',
            venue: {
              departementCode: '97',
            },
          },
          {
            id: 'o3',
            venue: {
              departementCode: '97',
            },
          },
          {
            id: 'o4',
            venue: {
              departementCode: '97',
            },
          },
          {
            id: 'o5',
            venue: {
              departementCode: '97',
            },
          },
          {
            id: 'o6',
            venue: {
              departementCode: '97',
            },
          },
        ],
        stocks: [
          {
            beginningDatetime: oneDayBeforeNow,
            id: 's1',
            offerId: 'o1',
          },
          {
            beginningDatetime: fourDaysAfterNow,
            id: 's2',
            offerId: 'o2',
          },
          {
            beginningDatetime: nineDaysAfterNow,
            id: 's3',
            offerId: 'o3',
          },
          {
            beginningDatetime: permanent,
            id: 's4',
            offerId: 'o4',
          },
          {
            beginningDatetime: nineDaysAfterNow,
            id: 's5',
            offerId: 'o5',
          },
          {
            beginningDatetime: nineDaysAfterNow,
            id: 's6',
            offerId: 'o6',
          },
        ],
      },
    }

    // when
    const results = selectUpComingBookings(state)

    // then
    expect(results).toStrictEqual([
      {
        id: 'b3',
        isCancelled: false,
        isUsed: false,
        stockId: 's3',
      },
      {
        id: 'b4',
        isCancelled: false,
        isUsed: false,
        stockId: 's4',
      },
    ])
  })
})

describe('selectFinishedBookings()', () => {
  it('should return finished bookings', () => {
    // given
    const state = {
      data: {
        bookings: [
          {
            id: 'b1',
            isCancelled: false,
            isEventExpired: false,
            stockId: 's1',
          },
          {
            id: 'b2',
            isCancelled: true,
            isEventExpired: false,
            stockId: 's2',
          },
          {
            id: 'b3',
            isCancelled: false,
            isEventExpired: false,
            stockId: 's3',
          },
          {
            id: 'b4',
            isCancelled: true,
            isEventExpired: false,
            stockId: 's4',
          },
          {
            id: 'b5',
            isCancelled: false,
            isEventExpired: true,
            stockId: 's5',
          },
        ],
        offers: [
          {
            id: 'o1',
            isNotBookable: false,
          },
          {
            id: 'o2',
            isNotBookable: false,
          },
          {
            id: 'o3',
            isNotBookable: true,
          },
          {
            id: 'o4',
            isNotBookable: true,
          },
          {
            id: 'o5',
            isNotBookable: false,
          },
        ],
        stocks: [
          {
            id: 's1',
            offerId: 'o1',
          },
          {
            id: 's2',
            offerId: 'o2',
          },
          {
            id: 's3',
            offerId: 'o3',
          },
          {
            id: 's4',
            offerId: 'o4',
          },
          {
            id: 's5',
            offerId: 'o5',
          },
        ],
      },
    }

    // when
    const results = selectFinishedBookings(state)

    // then
    expect(results).toStrictEqual([
      {
        id: 'b3',
        isCancelled: false,
        isEventExpired: false,
        stockId: 's3',
      },
      {
        id: 'b5',
        isCancelled: false,
        isEventExpired: true,
        stockId: 's5',
      },
    ])
  })
})

describe('selectCancelledBookings()', () => {
  it('should return cancelled bookings', () => {
    // given
    const state = {
      data: {
        bookings: [
          {
            id: 'b1',
            isCancelled: false,
          },
          {
            id: 'b2',
            isCancelled: true,
          },
        ],
      },
    }

    // when
    const results = selectCancelledBookings(state)

    // then
    expect(results).toStrictEqual([
      {
        id: 'b2',
        isCancelled: true,
      },
    ])
  })
})

describe('selectUsedBookings()', () => {
  it('should return used bookings', () => {
    // given
    const state = {
      data: {
        bookings: [
          {
            id: 'b1',
            isUsed: false,
          },
          {
            id: 'b2',
            isUsed: true,
          },
        ],
      },
    }

    // when
    const results = selectUsedBookings(state)

    // then
    expect(results).toStrictEqual([
      {
        id: 'b2',
        isUsed: true,
      },
    ])
  })
})

describe('selectBookingsOrderedByBeginningDateTimeAsc()', () => {
  it('should return bookings ordered by beginning date time', () => {
    // given
    jest.spyOn(Date, 'now').mockImplementation(() => '2000-01-01T20:00:00Z')
    const oneDayBeforeNow = new Date('1999-12-31T20:00:00.00Z').toISOString()
    const fourDaysAfterNow = new Date('2000-01-04T20:00:00.00Z').toISOString()
    const nineDaysAfterNow = new Date('2000-01-09T20:00:00.01Z').toISOString()
    const nineDaysAfterNowBis = new Date('2000-01-09T10:00:00.01Z').toISOString()
    const permanent = null
    const bookings = [
      {
        id: 'b1',
        stockId: 's1',
      },
      {
        id: 'b2',
        stockId: 's2',
      },
      {
        id: 'b3',
        stockId: 's3',
      },
      {
        id: 'b4',
        stockId: 's4',
      },
      {
        id: 'b5',
        stockId: 's5',
      },
      {
        id: 'b6',
        stockId: 's6',
      },
      {
        id: 'b7',
        stockId: 's7',
      },
    ]
    const state = {
      data: {
        offers: [
          {
            id: 'o1',
            venue: {
              departementCode: '97',
            },
          },
          {
            id: 'o2',
            venue: {
              departementCode: '97',
            },
          },
          {
            id: 'o3',
            venue: {
              departementCode: '97',
            },
          },
          {
            id: 'o4',
            venue: {
              departementCode: '97',
            },
          },
          {
            id: 'o5',
            venue: {
              departementCode: '97',
            },
          },
          {
            id: 'o6',
            venue: {
              departementCode: '97',
            },
          },
          {
            id: 'o7',
            venue: {
              departementCode: '97',
            },
          },
        ],
        stocks: [
          {
            beginningDatetime: oneDayBeforeNow,
            id: 's1',
            offerId: 'o1',
          },
          {
            beginningDatetime: fourDaysAfterNow,
            id: 's2',
            offerId: 'o2',
          },
          {
            beginningDatetime: nineDaysAfterNow,
            id: 's3',
            offerId: 'o3',
          },
          {
            beginningDatetime: permanent,
            id: 's4',
            offerId: 'o4',
          },
          {
            beginningDatetime: fourDaysAfterNow,
            id: 's5',
            offerId: 'o5',
          },
          {
            beginningDatetime: fourDaysAfterNow,
            id: 's6',
            offerId: 'o6',
          },
          {
            beginningDatetime: nineDaysAfterNowBis,
            id: 's7',
            offerId: 'o7',
          },
        ],
      },
    }

    // when
    const results = selectBookingsOrderedByBeginningDateTimeAsc(state, bookings)

    // then
    expect(results).toStrictEqual([
      {
        id: 'b1',
        stockId: 's1',
      },
      {
        id: 'b2',
        stockId: 's2',
      },
      {
        id: 'b5',
        stockId: 's5',
      },
      {
        id: 'b6',
        stockId: 's6',
      },
      {
        id: 'b7',
        stockId: 's7',
      },
      {
        id: 'b3',
        stockId: 's3',
      },
      {
        id: 'b4',
        stockId: 's4',
      },
    ])
  })
})

describe('selectFirstMatchingBookingByOfferId', () => {
  it('should return null when no stock', () => {
    // given
    const state = {
      data: {
        bookings: [{ id: 'AE', stockId: 'AE' }],
        stocks: [],
      },
    }

    // when
    const firstMatchingBooking = selectFirstMatchingBookingByOfferId(state)

    // then
    expect(firstMatchingBooking).toBeNull()
  })

  it('should return null when no bookings matching stock is found', () => {
    // given
    const state = {
      data: {
        bookings: [{ id: 'AA', stockId: 'AE', isCancelled: true }],
        stocks: [{ id: 'wrong id' }, { id: 'AE' }],
      },
    }

    // when
    const firstMatchingBooking = selectFirstMatchingBookingByOfferId(state)

    // then
    expect(firstMatchingBooking).toBeNull()
  })

  it('should return first not cancelled booking in the future', () => {
    // given
    const now = moment()
    const oneDayBeforeNow = now.subtract(1, 'days').format()
    const twoDaysAfterNow = now.add(2, 'days').format()
    const threeDaysAfterNow = now.add(3, 'days').format()

    const stocks = [
      { id: 'past stock', beginningDatetime: oneDayBeforeNow },
      { id: 'future stock 1', beginningDatetime: twoDaysAfterNow },
      { id: 'future stock 2', beginningDatetime: threeDaysAfterNow },
    ]
    const nextBooking = { id: 'AA', isCancelled: false, stockId: 'future stock 1' }
    const futureBooking = { id: 'BB', isCancelled: false, stockId: 'future stock 2' }
    const cancelledBooking = { id: 'CC', isCancelled: true, stockId: 'future stock 1' }
    const pastBooking = { id: 'DD', isCancelled: false, stockId: 'past stock' }
    const bookings = [cancelledBooking, futureBooking, nextBooking, pastBooking]
    const state = {
      data: {
        bookings,
        stocks,
      },
    }

    // when
    const firstMatchingBooking = selectFirstMatchingBookingByOfferId(state)

    // then
    expect(firstMatchingBooking).toStrictEqual(nextBooking)
  })
})

describe('selectBookingById', () => {
  it('should return undefined when no match', () => {
    // given
    const state = {
      data: {
        bookings: [{ id: 'foo' }, { id: 'bar' }, { id: 'baz' }],
      },
    }

    // when
    const result = selectBookingById(state, 'wrong')

    // then
    expect(result).toBeUndefined()
  })

  it('should return booking matching id', () => {
    // given
    const state = {
      data: {
        bookings: [{ id: 'foo' }, { id: 'bar' }, { id: 'baz' }],
      },
    }

    // when
    const result = selectBookingById(state, 'bar')

    // then
    expect(result).toStrictEqual({ id: 'bar' })
    expect(result).toBe(state.data.bookings[1])
  })
})

describe('selectBookingByRouterMatch', () => {
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
