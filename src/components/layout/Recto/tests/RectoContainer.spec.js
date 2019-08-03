import set from 'lodash.set'
import { getSelectorByCardPosition, mapStateToProps } from '../RectoContainer'

import currentRecommendationSelector from '../../../selectors/currentRecommendation/currentRecommendation'
import nextRecommendationSelector from '../../../selectors/nextRecommendation'
import previousRecommendationSelector from '../../../selectors/previousRecommendation'

describe('src | components | recto | RectoContainer', () => {
  describe('mapStateToProps returns required props for Recto components ', () => {
    it('when a recommendation is passed by component props, does not care about current position in props', () => {
      // given
      const state = {}
      set(state, 'card.areDetailsVisible', true)
      const props = {}
      set(props, 'position', 'previous')
      set(props, 'recommendation', 'AAAA')

      // when
      const result = mapStateToProps(state, props)

      // then
      const expected = {
        areDetailsVisible: true,
        recommendation: props.recommendation,
      }
      expect(result).toStrictEqual(expected)
    })
  })

  describe('getSelectorByCardPosition', () => {
    it('return currentRecommendationSelector', () => {
      // given
      const value = 'current'

      // when
      const result = getSelectorByCardPosition(value)

      // then
      const expected = currentRecommendationSelector
      expect(result).toStrictEqual(expected)
    })

    it('return previousRecommendationSelector', () => {
      // given
      const value = 'previous'

      // when
      const result = getSelectorByCardPosition(value)

      // then
      const expected = previousRecommendationSelector
      expect(result).toStrictEqual(expected)
    })

    it('return nextRecommendationSelector', () => {
      // given
      const value = 'next'

      // when
      const result = getSelectorByCardPosition(value)

      // then
      const expected = nextRecommendationSelector
      expect(result).toStrictEqual(expected)
    })

    it('return noop function if keyword is not valid', () => {
      // given
      const value = 'not a valid value'

      // when
      const result = getSelectorByCardPosition(value)

      // then
      expect(typeof result === 'function').toBe(true)
      expect(result).not.toStrictEqual(nextRecommendationSelector)
      expect(result).not.toStrictEqual(previousRecommendationSelector)
      expect(result).not.toStrictEqual(currentRecommendationSelector)
    })
  })
})
