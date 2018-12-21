// jest --env=jsdom ./src/components/pages/activation/tests/utils --watch
import { getQueryStringEmail, getURLTokenParam } from '../utils'

describe('src | components | pages | activation | tests | utils', () => {
  describe('utils.getURLTokenParam', () => {
    it('returns token if exists', () => {
      // given
      const token = 'AAAA'
      const value = { params: { token } }
      // when
      const result = getURLTokenParam(value)
      // then
      expect(result).toStrictEqual(token)
    })

    it('returns token equal to undefined if its value equal null', () => {
      // given
      const value = { params: { token: null } }
      // when
      const result = getURLTokenParam(value)
      // then
      expect(result).toStrictEqual(undefined)
    })

    it('returns token equal undefined if its value equal undefined', () => {
      // given
      const value = { params: { token: undefined } }
      // when
      const result = getURLTokenParam(value)
      // then
      expect(result).toStrictEqual(undefined)
    })

    it('returns token equal undefined if is not defined', () => {
      // given
      const value = { params: {} }
      // when
      const result = getURLTokenParam(value)
      // then
      expect(result).toStrictEqual(undefined)
    })

    it('returns token equal undefined if params is not defined', () => {
      // given
      const value = {}
      // when
      const result = getURLTokenParam(value)
      // then
      expect(result).toStrictEqual(undefined)
    })

    it('returns token equal null if match is not defined', () => {
      // when
      const result = getURLTokenParam()
      // then
      expect(result).toStrictEqual(undefined)
    })
  })
  describe('utils.getQueryStringEmail', () => {
    it('returns undefined if search is not defined', () => {
      // given
      const value = {}
      // when
      const result = getQueryStringEmail(value)
      // then
      expect(result).toStrictEqual(undefined)
    })

    it('returns null if match falsey', () => {
      // given
      const value = { search: false }
      // when
      const result = getQueryStringEmail(value)
      // then
      expect(result).toStrictEqual(undefined)
    })

    it('returns decoded email if is a string', () => {
      // given
      const email = 'any-encodé-email@gmail.com'
      const search = `?email=${encodeURI(email)}`
      // when
      const result = getQueryStringEmail({ search })
      // then
      expect(result).toStrictEqual(email)
    })

    it('returns undefined if search do not contains email key', () => {
      // given
      const email = 'any-encodé-email@gmail.com'
      const search = `?notemail=${encodeURI(email)}`
      // when
      const result = getQueryStringEmail({ search })
      // then
      expect(result).toStrictEqual(undefined)
    })

    it('returns undefined if search is not a string', () => {
      // given
      const search = encodeURI('any-encodé-email@gmail.com')
      // when
      const result = getQueryStringEmail({ search })
      // then
      expect(result).toStrictEqual(undefined)
    })
  })
})
