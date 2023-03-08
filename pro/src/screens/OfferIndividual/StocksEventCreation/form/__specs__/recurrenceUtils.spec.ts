import { getDatesInInterval } from '../recurrenceUtils'

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
})
