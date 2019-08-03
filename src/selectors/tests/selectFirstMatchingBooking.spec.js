import selectFirstMatchingBookingByStocks from '../selectFirstMatchingBookingByStocks'

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
})
