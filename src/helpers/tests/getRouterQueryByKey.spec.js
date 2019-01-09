// jest --env=jsdom ./src/helpers/tests/getRouterQueryByKey --watch
import getRouterQueryByKey from '../getRouterQueryByKey'

describe('src | helpers | tests | getRouterQueryByKey', () => {
  it('should thrown if missing location param', () => {
    expect(() => {
      // when
      getRouterQueryByKey({})
    }).toThrow()
  })

  it('should thrown if missing email param', () => {
    expect(() => {
      // when
      getRouterQueryByKey({ search: `?email=user@mail.com}` })
    }).toThrow()
  })

  it('returns null if match falsey', () => {
    // given
    const value = { search: false }
    // when
    const result = getRouterQueryByKey(value, 'email')
    // then
    expect(result).toStrictEqual(undefined)
  })

  it('returns decoded email if is a string', () => {
    // given
    const email = 'any-encodé-email@gmail.com'
    const search = `?email=${encodeURI(email)}`
    // when
    const result = getRouterQueryByKey({ search }, 'email')
    // then
    expect(result).toStrictEqual(email)
  })

  it('returns undefined if search do not contains email key', () => {
    // given
    const email = 'any-encodé-email@gmail.com'
    const search = `?notemail=${encodeURI(email)}`
    // when
    const result = getRouterQueryByKey({ search }, 'email')
    // then
    expect(result).toStrictEqual(undefined)
  })

  it('returns undefined if search is not a string', () => {
    // given
    const search = encodeURI('any-encodé-email@gmail.com')
    // when
    const result = getRouterQueryByKey({ search }, 'email')
    // then
    expect(result).toStrictEqual(undefined)
  })
})
