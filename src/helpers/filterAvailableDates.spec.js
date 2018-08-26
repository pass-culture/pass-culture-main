/* eslint no-console: 0, max-nested-callbacks: 0 */
import 'moment-timezone'
import moment from 'moment'
import { expect } from 'chai'
import { filterAvailableDates } from './filterAvailableDates'

const DEFAULT_TIMEZONE = 'Europe/Paris'
const inTwoDays = moment()
  .add(2, 'days')
  .tz(DEFAULT_TIMEZONE)
  .toISOString()
const inOneDay = moment()
  .add(1, 'days')
  .tz(DEFAULT_TIMEZONE)
  .toISOString()
const inToday = moment()
  .tz(DEFAULT_TIMEZONE)
  .toISOString()

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
    expect(expected).to.deep.equal(result)
  })
})
