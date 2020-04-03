import moment from 'moment'

import {
  selectBookingById,
  selectBookingByRouterMatch,
  selectBookingsOrderedByBeginningDateTimeAsc,
  selectCancelledBookings,
  selectEventBookingsOfTheWeek,
  selectFinishedEventBookings,
  selectFirstMatchingBookingByOfferId,
  selectPassedBookingsByOfferId,
  selectUpComingBookings,
  selectUsedThingBookings,
} from '../bookingsSelectors'

describe('selectEventBookingsOfTheWeek', () => {
  it('should return bookings of the week', () => {
    // given
    jest.spyOn(Date, 'now').mockImplementation(() => '2000-01-01T20:00:00Z')
    const stockYesterday = {
      beginningDatetime: new Date('1999-12-31T20:00:00.00Z').toISOString(),
      id: 's1',
      offerId: 'o1',
    }
    const stockToday = {
      beginningDatetime: new Date('2000-01-01T21:00:00Z').toISOString(),
      id: 's7',
      offerId: 'o1',
    }
    const stockInTwoDays = {
      beginningDatetime: new Date('2000-01-02T20:00:00.00Z').toISOString(),
      id: 's2',
      offerId: 'o1',
    }
    const stockInEightDays = {
      beginningDatetime: new Date('2000-01-08T20:00:00.01Z').toISOString(),
      id: 's6',
      offerId: 'o1',
    }
    const stockInNineDays = {
      beginningDatetime: new Date('2000-01-09T20:00:00.01Z').toISOString(),
      id: 's3',
      offerId: 'o1',
    }
    const stockPermanent = {
      beginningDatetime: null,
      id: 's4',
      offerId: 'o2',
    }
    const state = {
      data: {
        bookings: [
          {
            id: 'b1',
            isCancelled: false,
            isUsed: false,
            stockId: stockYesterday.id,
          },
          {
            id: 'b8',
            isCancelled: false,
            isUsed: false,
            stockId: stockToday.id,
          },
          {
            id: 'b7',
            isCancelled: false,
            isUsed: false,
            stockId: stockInEightDays.id,
          },
          {
            id: 'b2',
            isCancelled: false,
            isUsed: false,
            stockId: stockInTwoDays.id,
          },
          {
            id: 'b5',
            isCancelled: true,
            isUsed: false,
            stockId: stockInTwoDays.id,
          },
          {
            id: 'b6',
            isCancelled: false,
            isUsed: true,
            stockId: stockInTwoDays.id,
          },
          {
            id: 'b3',
            isCancelled: false,
            isUsed: false,
            stockId: stockInNineDays.id,
          },
          {
            id: 'b4',
            isCancelled: false,
            isUsed: false,
            stockId: stockPermanent.id,
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
        ],
        stocks: [
          stockYesterday,
          stockToday,
          stockInTwoDays,
          stockInEightDays,
          stockInNineDays,
          stockPermanent,
        ],
      },
    }

    // when
    const bookings = selectEventBookingsOfTheWeek(state)

    // then
    expect(bookings).toStrictEqual([
      {
        id: 'b8',
        isCancelled: false,
        isUsed: false,
        stockId: stockToday.id,
      },
      {
        id: 'b2',
        isCancelled: false,
        isUsed: false,
        stockId: stockInTwoDays.id,
      },
      {
        id: 'b6',
        isCancelled: false,
        isUsed: true,
        stockId: stockInTwoDays.id,
      },
      {
        id: 'b7',
        isCancelled: false,
        isUsed: false,
        stockId: stockInEightDays.id,
      },
    ])
  })
})

describe('selectUpComingBookings', () => {
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
    const bookings = selectUpComingBookings(state)

    // then
    expect(bookings).toStrictEqual([
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

describe('selectFinishedEventBookings', () => {
  describe('when bookings are on non cancelled events', () => {
    it('should return expired bookings that are not bookable', () => {
      // given
      const state = {
        data: {
          bookings: [
            {
              id: 'b1',
              isCancelled: false,
              isEventExpired: true,
              stockId: 's1',
            },
          ],
          offers: [
            {
              id: 'o1',
              hasBookingLimitDatetimesPassed: true,
              isEvent: true,
            },
          ],
          stocks: [
            {
              id: 's1',
              offerId: 'o1',
            },
          ],
        },
      }

      // when
      const bookings = selectFinishedEventBookings(state)

      // then
      expect(bookings).toStrictEqual([
        {
          id: 'b1',
          isCancelled: false,
          isEventExpired: true,
          stockId: 's1',
        },
      ])
    })

    it('should return expired bookings', () => {
      // given
      const state = {
        data: {
          bookings: [
            {
              id: 'b1',
              isCancelled: false,
              isEventExpired: true,
              stockId: 's1',
            },
          ],
          offers: [
            {
              id: 'o1',
              hasBookingLimitDatetimesPassed: false,
              isEvent: true,
            },
          ],
          stocks: [
            {
              id: 's1',
              offerId: 'o1',
            },
          ],
        },
      }

      // when
      const bookings = selectFinishedEventBookings(state)

      // then
      expect(bookings).toStrictEqual([
        {
          id: 'b1',
          isCancelled: false,
          isEventExpired: true,
          stockId: 's1',
        },
      ])
    })

    it('should not return upcoming bookings that are not bookable', () => {
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
          ],
          offers: [
            {
              id: 'o1',
              hasBookingLimitDatetimesPassed: false,
              isEvent: true,
            },
          ],
          stocks: [
            {
              id: 's1',
              offerId: 'o1',
            },
          ],
        },
      }

      // when
      const bookings = selectFinishedEventBookings(state)

      // then
      expect(bookings).toHaveLength(0)
    })

    it('should not return upcomings bookings that are still bookable', () => {
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
          ],
          offers: [
            {
              id: 'o1',
              hasBookingLimitDatetimesPassed: false,
              isEvent: true,
            },
          ],
          stocks: [
            {
              id: 's1',
              offerId: 'o1',
            },
          ],
        },
      }

      // when
      const bookings = selectFinishedEventBookings(state)

      // then
      expect(bookings).toStrictEqual([])
    })
  })
  describe('when bookings are cancelled or on things', () => {
    it('should not return bookings on thing types', () => {
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
          ],
          offers: [
            {
              id: 'o1',
              hasBookingLimitDatetimesPassed: true,
              isEvent: false,
            },
          ],
          stocks: [
            {
              id: 's1',
              offerId: 'o1',
            },
          ],
        },
      }

      // when
      const bookings = selectFinishedEventBookings(state)

      // then
      expect(bookings).toStrictEqual([])
    })

    it('should not return cancelled bookings', () => {
      // given
      const state = {
        data: {
          bookings: [
            {
              id: 'b1',
              isCancelled: true,
              isEventExpired: false,
              stockId: 's1',
            },
          ],
          offers: [
            {
              id: 'o1',
              hasBookingLimitDatetimesPassed: true,
              isEvent: true,
            },
          ],
          stocks: [
            {
              id: 's1',
              offerId: 'o1',
            },
          ],
        },
      }

      // when
      const bookings = selectFinishedEventBookings(state)

      // then
      expect(bookings).toStrictEqual([])
    })
  })
})

describe('selectCancelledBookings', () => {
  it('should return cancelled bookings', () => {
    // given
    const state = {
      data: {
        bookings: [
          {
            id: 'b1',
            isCancelled: true,
          },
        ],
      },
    }

    // when
    const bookings = selectCancelledBookings(state)

    // then
    expect(bookings).toStrictEqual([
      {
        id: 'b1',
        isCancelled: true,
      },
    ])
  })

  it('should not return bookings that are not cancelled', () => {
    // given
    const state = {
      data: {
        bookings: [
          {
            id: 'b1',
            isCancelled: false,
          },
        ],
      },
    }

    // when
    const bookings = selectCancelledBookings(state)

    // then
    expect(bookings).toStrictEqual([])
  })
})

describe('selectUsedThingBookings', () => {
  it('should not return bookings on events', () => {
    // given
    jest.spyOn(Date, 'now').mockImplementation(() => '2000-01-01T20:00:00Z')
    const state = {
      data: {
        bookings: [
          {
            id: 'b1',
            isUsed: true,
            stockId: 's1',
          },
        ],
        stocks: [
          {
            beginningDatetime: new Date('1999-12-31T20:00:00.00Z').toISOString(),
            id: 's1',
          },
        ],
      },
    }

    // when
    const bookings = selectUsedThingBookings(state)

    // then
    expect(bookings).toStrictEqual([])
  })

  it('should not return bookings on unused things', () => {
    // given
    const state = {
      data: {
        bookings: [
          {
            id: 'b1',
            isUsed: false,
            stockId: 's1',
          },
        ],
        stocks: [
          {
            beginningDatetime: null,
            id: 's1',
          },
        ],
      },
    }

    // when
    const bookings = selectUsedThingBookings(state)

    // then
    expect(bookings).toStrictEqual([])
  })

  it('should return booking on used things', () => {
    // given
    const state = {
      data: {
        bookings: [
          {
            id: 'b1',
            isUsed: true,
            stockId: 's1',
          },
        ],
        stocks: [
          {
            beginningDatetime: null,
            id: 's1',
          },
        ],
      },
    }

    // when
    const bookings = selectUsedThingBookings(state)

    // then
    expect(bookings).toStrictEqual([
      {
        id: 'b1',
        isUsed: true,
        stockId: 's1',
      },
    ])
  })
})

describe('selectBookingsOrderedByBeginningDateTimeAsc', () => {
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
    const selectedBookings = selectBookingsOrderedByBeginningDateTimeAsc(state, bookings)

    // then
    expect(selectedBookings).toStrictEqual([
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
    const booking = selectBookingById(state, 'wrong')

    // then
    expect(booking).toBeUndefined()
  })

  it('should return booking matching id', () => {
    // given
    const state = {
      data: {
        bookings: [{ id: 'foo' }, { id: 'bar' }, { id: 'baz' }],
      },
    }

    // when
    const booking = selectBookingById(state, 'bar')

    // then
    expect(booking).toStrictEqual({ id: 'bar' })
    expect(booking).toBe(state.data.bookings[1])
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
    const booking = selectBookingByRouterMatch(state, match)

    // then
    expect(booking).toStrictEqual({ id: 'AE' })
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
    const booking = selectBookingByRouterMatch(state, match)

    // then
    expect(booking).toStrictEqual({ id: 'AE', stockId: 'CG' })
  })
})

describe('selectPassedBookingsByOfferId', () => {
  it('should return empty when no booking', () => {
    // given
    const state = {
      data: {
        offer: [{ id: 'A1' }],
        stocks: [{ id: 'B1', offerId: 'A1' }],
        bookings: [],
      },
    }

    // when
    const passedBookings = selectPassedBookingsByOfferId(state, 'A1')

    // then
    expect(passedBookings).toStrictEqual([])
  })

  it('should return empty when no bookings matching offer', () => {
    // given
    const state = {
      data: {
        offer: [{ id: 'A1' }],
        stocks: [{ id: 'B1', offerId: 'A1' }, { id: 'B2', offerId: 'A1' }],
        bookings: [{ id: 'C1', stockId: 'E1' }],
      },
    }

    // when
    const passedBookings = selectPassedBookingsByOfferId(state, 'A1')

    // then
    expect(passedBookings).toStrictEqual([])
  })

  it('should return not cancelled bookings in the passed', () => {
    // given
    const now = moment()
    const oneDayBeforeNow = now.subtract(1, 'days').format()
    const state = {
      data: {
        offer: [{ id: 'A1' }],
        stocks: [{ id: 'B1', offerId: 'A1', beginningDatetime: oneDayBeforeNow }],
        bookings: [{ id: 'C1', stockId: 'B1', isCancelled: false }],
      },
    }

    // when
    const passedBookings = selectPassedBookingsByOfferId(state, 'A1')

    // then
    expect(passedBookings).toStrictEqual([{ id: 'C1', stockId: 'B1', isCancelled: false }])
  })

  it('should not return cancelled bookings', () => {
    // given
    const now = moment()
    const oneDayBeforeNow = now.subtract(1, 'days').format()
    const state = {
      data: {
        offer: [{ id: 'A1' }],
        stocks: [{ id: 'B1', offerId: 'A1', beginningDatetime: oneDayBeforeNow }],
        bookings: [{ id: 'C1', stockId: 'B1', isCancelled: true }],
      },
    }

    // when
    const passedBookings = selectPassedBookingsByOfferId(state, 'A1')

    // then
    expect(passedBookings).toStrictEqual([])
  })

  it('should not return valid bookings in the future', () => {
    // given
    const now = moment()
    const oneDayAfterNow = now.add(1, 'days').format()
    const state = {
      data: {
        offer: [{ id: 'A1' }],
        stocks: [{ id: 'B1', offerId: 'A1', beginningDatetime: oneDayAfterNow }],
        bookings: [{ id: 'C1', stockId: 'B1', isCancelled: false }],
      },
    }

    // when
    const passedBookings = selectPassedBookingsByOfferId(state, 'A1')

    // then
    expect(passedBookings).toStrictEqual([])
  })
})
