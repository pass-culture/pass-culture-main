import moment from 'moment'

import selectFirstMatchingBookingByStocks from '../selectFirstMatchingBookingByStocks'

describe('src | selectors | selectFirstMatchingBookingByStocks', () => {
  it('should return null when no stock', () => {
    // given
    const state = {
      data: {
        bookings: [{ id: 'AE', stockId: 'AE' }],
        stocks: [],
      },
    }

    // when
    const firstMatchingBooking = selectFirstMatchingBookingByStocks(state)

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
    const firstMatchingBooking = selectFirstMatchingBookingByStocks(state)

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
      { id: 'past stock', beginningDateTime: oneDayBeforeNow },
      { id: 'future stock 1', beginningDateTime: twoDaysAfterNow },
      { id: 'future stock 2', beginningDateTime: threeDaysAfterNow },
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
    const firstMatchingBooking = selectFirstMatchingBookingByStocks(state)

    // then
    expect(firstMatchingBooking).toStrictEqual(nextBooking)
  })
})
