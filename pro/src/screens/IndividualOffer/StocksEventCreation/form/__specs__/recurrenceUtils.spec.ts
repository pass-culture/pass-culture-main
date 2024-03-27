import { getDatesInInterval, isTimeInTheFuture } from '../recurrenceUtils'
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

describe('isTimeInTheFuture', () => {
  beforeEach(() => {
    vi.useFakeTimers()
    vi.setSystemTime(new Date('2010-01-01 13:15'))
  })

  afterEach(() => {
    vi.useRealTimers()
  })

  it('should return true for future dates', () => {
    expect(isTimeInTheFuture(new Date('2020-03-03'), '11:00')).toBe(true)
  })

  it('should return false for past dates', () => {
    expect(isTimeInTheFuture(new Date('2000-03-03'), '11:00')).toBe(false)
  })

  it('should return true for today and future hours', () => {
    expect(isTimeInTheFuture(new Date('2010-01-01'), '14:00')).toBe(true)
  })

  it('should return true for today and past hours', () => {
    expect(isTimeInTheFuture(new Date('2010-01-01'), '10:00')).toBe(false)
  })

  it('should return true for today, current hour and future minutes', () => {
    expect(isTimeInTheFuture(new Date('2010-01-01'), '13:20')).toBe(true)
  })

  it('should return false for today, current hour and past minutes', () => {
    expect(isTimeInTheFuture(new Date('2010-01-01'), '13:00')).toBe(false)
  })

  it('should return false for exact same time', () => {
    expect(isTimeInTheFuture(new Date('2010-01-01'), '13:15')).toBe(false)
  })
})
