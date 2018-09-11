/* eslint no-console: 0, max-nested-callbacks: 0 */
import 'moment-timezone'
import moment from 'moment'
import { filterAvailableDates } from './filterAvailableDates'

const inTwoDays = moment().add(2, 'days')
const inOneDay = moment().add(1, 'days')
const inToday = moment()

describe('filterAvailableDates', () => {
  it('filtre les dates passées ou du jour même', () => {
    const stocks = [
      { bookingLimitDatetime: inTwoDays },
      { bookingLimitDatetime: inOneDay },
      { bookingLimitDatetime: inToday },
    ]
    const expected = [
      { bookingLimitDatetime: inTwoDays },
      { bookingLimitDatetime: inOneDay },
    ]
    const result = filterAvailableDates(stocks)
    expect(expected).toStrictEqual(result)
  })
})
