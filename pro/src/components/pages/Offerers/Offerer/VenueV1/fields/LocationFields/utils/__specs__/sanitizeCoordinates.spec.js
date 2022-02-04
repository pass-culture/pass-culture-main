import sanitizeCoordinates from '../sanitizeCoordinates'

describe('components | pages | Venue | GeoFields | sanitizeCoordinates', () => {
  it('should return 0 with invalid input', () => {
    // given
    let input = 'ABC'
    // when
    let result = sanitizeCoordinates(input)
    // then
    expect(result).toBe(0)
  })
  it('should return a number when given an int', () => {
    // given
    let input = 32
    // when
    let result = sanitizeCoordinates(input)
    // then
    expect(result).toStrictEqual(input)
    expect(typeof result).toBe('number')
  })
  it('should return a number when given a float', () => {
    // given
    let input = 32.2
    // when
    let result = sanitizeCoordinates(input)
    // then
    expect(result).toStrictEqual(input)
    expect(typeof result).toBe('number')
  })
  it('should return a number when string representing a float', () => {
    // given
    let input = '32.2'
    // when
    let result = sanitizeCoordinates(input)
    // then
    expect(result).toBe(32.2)
    expect(typeof result).toBe('number')
  })
  it('should translate french notation (coma) to english (dot)', () => {
    // given
    let input = '32,2'
    // when
    let result = sanitizeCoordinates(input)
    // then
    expect(result).toBe(32.2)
    expect(typeof result).toBe('number')
  })
  it('should ignore and remove special chars', () => {
    // given
    let input = '32;2'
    // when
    let result = sanitizeCoordinates(input)
    // then
    expect(result).toBe(322)
    expect(typeof result).toBe('number')
  })
  it('should return negative value for negative string value with dot', () => {
    // given
    let input = '-32.2'
    // when
    let result = sanitizeCoordinates(input)
    // then
    expect(result).toStrictEqual(-32.2)
    expect(typeof result).toBe('number')
  })
  it('should return negative value for negative string value with comma', () => {
    // given
    let input = '-32,2'
    // when
    let result = sanitizeCoordinates(input)
    // then
    expect(result).toStrictEqual(-32.2)
    expect(typeof result).toBe('number')
  })
})
