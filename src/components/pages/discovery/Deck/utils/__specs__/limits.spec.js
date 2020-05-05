import { getNextLimit, NB_CARDS_REMAINING_THAT_TRIGGERS_LOAD } from '../limits'

describe('src | components | pages | discovery | Deck | utils | limits', () => {
  describe('nextLimit', () => {
    it('when number of recommendations is equal to 0', () => {
      // given
      const nbRecommendations = 0

      // when
      const result = getNextLimit(nbRecommendations)

      // then
      expect(result).toStrictEqual(false)
    })

    it('when number of recommendations is equal to 1', () => {
      // given
      const nbRecommendations = 1

      // when
      const result = getNextLimit(nbRecommendations)

      // then
      expect(result).toStrictEqual(0)
    })

    it('when number of recommendations is equal to 2', () => {
      // given
      const nbRecommendations = 2

      // when
      const result = getNextLimit(nbRecommendations)

      // then
      expect(result).toStrictEqual(1)
    })

    it('when number of recommendations is equal to max number of cards before load', () => {
      // given
      // when
      const result = getNextLimit(NB_CARDS_REMAINING_THAT_TRIGGERS_LOAD)

      // then
      expect(result).toStrictEqual(4)
    })

    it('when number of recommendations is superior to max number of cards before load by 1', () => {
      // given
      const nbRecommendations = NB_CARDS_REMAINING_THAT_TRIGGERS_LOAD + 1

      // when
      const result = getNextLimit(nbRecommendations)

      // then
      expect(result).toStrictEqual(5)
    })

    it('when number of recommendations is superior to max number of cards before load by 10', () => {
      // given
      const nbRecommendations = NB_CARDS_REMAINING_THAT_TRIGGERS_LOAD + 10

      // when
      const result = getNextLimit(nbRecommendations)

      // then
      expect(result).toStrictEqual(9)
    })
  })
})
