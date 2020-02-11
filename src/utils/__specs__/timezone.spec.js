import { formatLocalTimeDateString, getTimezone } from '../timezone'

describe('formatLocalTimeDateString', () => {
  it('should return a formatted date with Paris departement code and specified format', () => {
    // given
    const date = '2019-02-28T21:59:00Z'
    const departementCode = '75'
    const dateFormat = 'dddd D MMMM YYYY, HH:mm'

    // when
    const formattedDate = formatLocalTimeDateString(date, departementCode, dateFormat)

    // then
    expect(formattedDate).toBe('Thursday 28 February 2019, 22:59')
  })

  it('should return a formatted date with Cayenne departement code and specified format', () => {
    // given
    const date = '2019-02-28T21:59:00Z'
    const departementCode = '973'
    const dateFormat = 'dddd D MMMM YYYY, HH:mm'

    // when
    const formattedDate = formatLocalTimeDateString(date, departementCode, dateFormat)

    // then
    expect(formattedDate).toBe('Thursday 28 February 2019, 18:59')
  })

  it('should return a formatted date with Cayenne departement code and default format', () => {
    // given
    const date = '2019-02-28T21:59:00Z'
    const departementCode = '97'

    // when
    const formattedDate = formatLocalTimeDateString(date, departementCode)

    // then
    expect(formattedDate).toBe('Thursday 28/02/2019 à 18:59')
  })
})

describe('getTimezone', () => {
  it('should return Paris timezone for Paris', () => {
    // given
    const departementCode = '75'

    // when
    const timezone = getTimezone(departementCode)

    // then
    expect(timezone).toBe('Europe/Paris')
  })

  it('should return Cayenne timezone for 973', () => {
    // given
    const departementCode = '973'

    // when
    const timezone = getTimezone(departementCode)

    // then
    expect(timezone).toBe('America/Cayenne')
  })

  it('should return Cayenne timezone for 97', () => {
    // given
    const departementCode = '97'

    // when
    const timezone = getTimezone(departementCode)

    // then
    expect(timezone).toBe('America/Cayenne')
  })
})
