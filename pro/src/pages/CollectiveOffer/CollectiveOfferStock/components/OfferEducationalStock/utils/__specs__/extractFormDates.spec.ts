import { extractFormDates } from '../extractFormDates'

const emptyCollectiveStockFormDates = {
  startDate: '',
  endDate: '',
  eventTime: '',
  bookingLimitDate: '',
}

describe('extractFormDates', () => {
  it('should return default values when collectiveStock is not defined', () => {
    expect(extractFormDates({})).toStrictEqual(emptyCollectiveStockFormDates)
  })

  it('should return stock details', () => {
    const startDatetime = '2023-02-23T10:46:20Z'
    const endDatetime = '2023-02-23T10:46:20Z'
    const bookingLimitDatetime = '2023-02-28T10:46:20Z'

    expect(
      extractFormDates(
        { startDatetime, endDatetime, bookingLimitDatetime },
        '75'
      )
    ).toStrictEqual({
      bookingLimitDate: '2023-02-28',
      startDate: '2023-02-23',
      endDate: '2023-02-23',
      eventTime: '11:46',
    })
  })

  it('should not set eventTime when startDatetime is only a date (not a datetime)', () => {
    const startDatetime = '2030-07-30'

    expect(extractFormDates({ startDatetime }, '75')).toStrictEqual({
      ...emptyCollectiveStockFormDates,
      startDate: '2030-07-30',
    })
  })
})
