import moment from 'moment'
import filterPassedBookingLimitDatetimeStocks from '../filterPassedBookingLimitDatetimeStocks'

describe('src | filterPassedBookingLimitDatetimeStocks', () => {
  it('should return an array without null items', () => {
    // given
    const stocks = [{}, null, {}]

    // when
    const result = filterPassedBookingLimitDatetimeStocks(stocks)

    // then
    expect(result).toStrictEqual([{}, {}])
  })

  it('should return an array containing stocks with booking limit datetime after now only', () => {
    // given
    const bookingLimitDatetimeOneDayAfterNow = moment().add(2, 'days')
    const bookingLimitDatetimeOneDayBeforeNow = moment().subtract(2, 'days')
    const stocks = [
      { bookingLimitDatetime: bookingLimitDatetimeOneDayAfterNow },
      { bookingLimitDatetime: bookingLimitDatetimeOneDayBeforeNow },
    ]

    // when
    const result = filterPassedBookingLimitDatetimeStocks(stocks)

    // then
    expect(result).toHaveLength(1)
    expect(result).toStrictEqual([{ bookingLimitDatetime: bookingLimitDatetimeOneDayAfterNow }])
  })
})
