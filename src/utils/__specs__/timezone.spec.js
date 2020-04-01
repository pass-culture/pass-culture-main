import timezone, { setTimezoneOnBeginningDatetime } from '../timezone'

describe('src | utils | strings | timezone', () => {
  it('should return America/Cayenne when departementCode is 97', () => {
    expect(timezone('97')).toStrictEqual('America/Cayenne')
  })

  it('should return America/Cayenne when departementCode is 973', () => {
    expect(timezone('973')).toStrictEqual('America/Cayenne')
  })

  it('should return Europe/Paris by default', () => {
    expect(timezone('')).toStrictEqual('Europe/Paris')
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
