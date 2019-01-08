// jest --env=jsdom ./src/components/pages/activation/events/tests/connect --watch
import { mapStateToProps } from '../connect'

describe('src | components | pages | activation | events | connect', () => {
  describe('mapStateToProps', () => {
    it('should return empty array if no data', () => {
      // given
      const state = {}

      // when
      const result = mapStateToProps(state)

      // then
      const expected = { offers: [] }
      expect(result).toStrictEqual(expected)
    })
    it('should return empty array if no offers', () => {
      // given
      const data = { offers: null }
      const state = { data }

      // when
      const result = mapStateToProps(state)

      // then
      const expected = { offers: [] }
      expect(result).toStrictEqual(expected)
    })
  })
})
