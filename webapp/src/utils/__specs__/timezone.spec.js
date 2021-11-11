import { getTimezone, getTimezoneFromOffer, setTimezoneOnBeginningDatetime } from '../timezone'

describe('getTimezone', () => {
  it('should return America/Cayenne when departement code is 973', () => {
    expect(getTimezone('973')).toBe('America/Cayenne')
  })

  it('should return Indian/Reunion when departement code is 974', () => {
    expect(getTimezone('974')).toBe('Indian/Reunion')
  })

  it('should return Europe/Paris by default', () => {
    expect(getTimezone('')).toBe('Europe/Paris')
  })
})

describe('getTimezoneFromOffer', () => {
  it('should return America/Cayenne when departement code is 973', () => {
    // given
    const offer = {
      venue: {
        departementCode: '973',
      },
    }

    // when
    const result = getTimezoneFromOffer(offer)

    // then
    expect(result).toBe('America/Cayenne')
  })

  it('should return Indian/Reunion when departement code is 974', () => {
    // given
    const offer = {
      venue: {
        departementCode: '974',
      },
    }

    // when
    const result = getTimezoneFromOffer(offer)

    // then
    expect(result).toBe('Indian/Reunion')
  })

  it('should return Europe/Paris by default', () => {
    // given
    const offer = {
      venue: {
        departementCode: 'Other Department',
      },
    }
    // when
    const result = getTimezoneFromOffer(offer)

    // then
    expect(result).toBe('Europe/Paris')
  })
})

describe('setTimezoneOnBeginningDatetime', () => {
  it('does nothing if stock as no beginning', () => {
    // given
    const stockWithoutDates = {
      quantity: 10,
      beginningDatetime: null,
      bookingLimitDatetime: null,
      endDatetime: null,
      id: 'C3LA',
      isSoftDeleted: false,
      modelName: 'Stock',
      offerId: 'ATRQ',
      price: 25.0,
    }
    const items = [stockWithoutDates]
    const timezone = 'Europe/Paris'

    // when
    const results = setTimezoneOnBeginningDatetime(timezone)(items)

    // then
    expect(results[0].offerId).toBe('ATRQ')
    expect(results[0].beginningDatetime).toBeNull()
    expect(results[0].endDatetime).toBeNull()
  })

  it('sets timezones to beginningDatetime', () => {
    // given
    const stockWithDate = {
      quantity: 10,
      beginningDatetime: '2019-04-19T18:30:00Z',
      bookingLimitDatetime: null,
      endDatetime: '2019-04-20T20:00:00Z',
      id: 'C3LA',
      isSoftDeleted: false,
      modelName: 'Stock',
      offerId: 'BYAQ',
      price: 25.0,
    }
    const items = [stockWithDate]
    const timezone = 'Europe/Paris'

    // when
    const results = setTimezoneOnBeginningDatetime(timezone)(items)

    // then
    expect(results[0].offerId).toBe('BYAQ')
    expect(results[0].beginningDatetime.format()).toBe('2019-04-19T20:30:00+02:00')
    expect(results[0].endDatetime).toBe('2019-04-20T20:00:00Z')
  })
})
