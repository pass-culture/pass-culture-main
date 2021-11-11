import showTypes from './showTypes'
import selectShowTypeByCode from '../selectShowTypeByCode'

const state = { data: { showTypes } }

describe('src | components | layout | Verso | VersoContent | VersoContentOffer | selectors | selectShowTypeByCode', () => {
  describe('when the code is valid', () => {
    it('should return the show sub type', () => {
      // given
      const code = 100

      // when
      const showType = selectShowTypeByCode(state, String(code))

      // then
      expect(showType.code).toStrictEqual(code)
    })
  })

  describe('when the code is not valid', () => {
    it('should return undefined', () => {
      // given
      const code = 666

      // when
      const showType = selectShowTypeByCode(state, String(code))

      // then
      expect(showType).toBeUndefined()
    })
  })
})
