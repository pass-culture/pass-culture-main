import { getDatesInInterval } from '../recurrenceUtils'
import { RecurrenceDays } from '../types'

describe('getDatesInInterval', () => {
  it('should return an empty array when start date is after end date', () => {
    expect(
      getDatesInInterval(new Date('2020-03-03'), new Date('2020-03-02'))
    ).toStrictEqual([])
  })

  it('should return an array with one date when start date is equal to end date', () => {
    expect(
      getDatesInInterval(new Date('2020-03-03'), new Date('2020-03-03'))
    ).toStrictEqual([new Date('2020-03-03')])
  })

  it('should return an array with all dates between start date and end date', () => {
    expect(
      getDatesInInterval(new Date('2020-03-03'), new Date('2020-03-06'))
    ).toStrictEqual([
      new Date('2020-03-03'),
      new Date('2020-03-04'),
      new Date('2020-03-05'),
      new Date('2020-03-06'),
    ])
  })

  it('should return only selected days', () => {
    expect(
      getDatesInInterval(new Date('2020-03-03'), new Date('2020-03-20'), [
        RecurrenceDays.SATURDAY,
        RecurrenceDays.SUNDAY,
      ])
    ).toStrictEqual([
      // Those are only saturdays and sundays
      new Date('2020-03-07'),
      new Date('2020-03-08'),
      new Date('2020-03-14'),
      new Date('2020-03-15'),
    ])
  })
})
