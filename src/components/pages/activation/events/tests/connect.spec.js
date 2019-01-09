// jest --env=jsdom ./src/components/pages/activation/events/tests/connect --watch
import { mapStateToProps } from '../connect'

describe('src | components | pages | activation | events | connect', () => {
  describe('mapStateToProps', () => {
    it('should return empty array if no data', () => {
      // given
      const state = {}
      const props = { location: { search: '?from=password' } }

      // when
      const result = mapStateToProps(state, props)

      // then
      const expected = { fromPassword: true, offers: [] }
      expect(result).toStrictEqual(expected)
    })
    it('should return empty array if no offers', () => {
      // given
      const data = { offers: null }
      const state = { data }
      const props = { location: { search: '?from=password' } }

      // when
      const result = mapStateToProps(state, props)

      // then
      const expected = { fromPassword: true, offers: [] }
      expect(result).toStrictEqual(expected)
    })
  })
})
