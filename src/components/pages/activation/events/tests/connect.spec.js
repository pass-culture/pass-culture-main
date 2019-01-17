// jest --env=jsdom ./src/components/pages/activation/events/tests/connect --watch
import { mapStateToProps } from '../connect'

import validOffers from './data/valid-offers.json'
import notValidOffers from './data/not-valid-offers.json'
import expectedGroupedOffers from './data/expected-grouped-offers.json'

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
    it('should return an array of grouped offers', () => {
      // given
      const data = { offers: [...validOffers, ...notValidOffers] }
      const state = { data }
      const props = { location: { search: '?from=password' } }

      // when
      const result = mapStateToProps(state, props)

      // then
      const expected = {
        fromPassword: true,
        offers: [...expectedGroupedOffers],
      }
      expect(result).toStrictEqual(expected)
    })
  })
})
