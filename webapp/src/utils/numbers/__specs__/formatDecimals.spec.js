import formatDecimals from '../formatDecimals'

describe('utils | formatDecimals', () => {
  it('returns a value with two decimals when number has two decimal digits', () => {
    // given
    const number = 476.98

    // when
    const result = formatDecimals(number)

    // then
    expect(result).toStrictEqual('476,98')
  })

  it('returns a value with two decimals when number has one decimal digits', () => {
    // given
    const number = 476.9

    // when
    const result = formatDecimals(number)

    // then
    expect(result).toStrictEqual('476,90')
  })

  it('returns a value with no decimals when number has no decimal digits', () => {
    // given
    const number = 476

    // when
    const result = formatDecimals(number)

    // then
    expect(result).toStrictEqual('476')
  })

  it('returns a value with no decimals when number has double zero decimal digits', () => {
    // given
    const number = 476.0

    // when
    const result = formatDecimals(number)

    // then
    expect(result).toStrictEqual('476')
  })

  it('returns exactly two decimals when number has many decimal digits', () => {
    // given
    const number = 231.38000001

    // then
    const result = formatDecimals(number)

    // when
    expect(result).toBe('231,38')
  })

  it('returns exactly 0 when balance has number is null', () => {
    // given
    const number = null

    // then
    const result = formatDecimals(number)

    // when
    expect(result).toBe('0')
  })

  it('returns exactly 0 when balance has number is 0', () => {
    // given
    const number = 0

    // then
    const result = formatDecimals(number)

    // when
    expect(result).toBe('0')
  })
})
