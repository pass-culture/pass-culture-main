import selectFirstMatchingBookingByStocks from '../selectFirstMatchingBookingByStocks'
import moment from 'moment'

describe('src | selectors | selectFirstMatchingBookingByStocks', () => {
  it('should return null when no found matching booking compared to its stock', () => {
    // given
    const stockId = 'wrong id'
    const bookings = [{ id: 'AE', stockId: 'AE' }]
    const stocks = [{ id: stockId }]
    const state = {
      data: {
        bookings,
      },
    }

    // when
    const firstMatchingBooking = selectFirstMatchingBookingByStocks(state, stocks)

    // then
    expect(firstMatchingBooking).toBeUndefined()
  })

  it('should return the not cancelled booking matching the first found stockId in stocks', () => {
    // given
    const stockId = 'BF'
    const matchingBooking = { id: 'AE', isCancelled: false, stockId }
    const otherBooking = { id: 'ABF', isCancelled: true, stockId }
    const oneotherBooking = { id: 'ABG', isCancelled: true, stockId }
    const bookings = [oneotherBooking, matchingBooking, otherBooking]
    const stocks = [{ id: stockId }]
    const state = {
      data: {
        bookings,
      },
    }

    // when
    const firstMatchingBooking = selectFirstMatchingBookingByStocks(state, stocks)

    // then
    expect(firstMatchingBooking).toStrictEqual(matchingBooking)
  })

  it('should return the cancelled booking matching the first found stockId in stocks if no isCancelled booking', () => {
    // given
    const stockId = 'BF'
    const matchingBooking = { id: 'AE', isCancelled: true, stockId }
    const otherBooking = { id: 'ABF', isCancelled: true, stockId }
    const bookings = [matchingBooking, otherBooking]
    const stocks = [{ id: stockId }]
    const state = {
      data: {
        bookings,
      },
    }

    // when
    const firstMatchingBooking = selectFirstMatchingBookingByStocks(state, stocks)

    // then
    expect(firstMatchingBooking).toStrictEqual(matchingBooking)
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
    const firstMatchingBooking = selectFirstMatchingBookingByStocks(state, stocks)

    // then
    expect(firstMatchingBooking).toStrictEqual(nextBooking)
  })
})
