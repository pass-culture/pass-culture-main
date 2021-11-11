import showTypes from './showTypes'
import selectShowSubTypeByCodeAndSubCode from '../selectShowSubTypeByCodeAndSubCode'

const state = { data: { showTypes } }

describe('src | components | layout | Verso | VersoContent | VersoContentOffer | selectors | selectShowSubTypeByCodeAndSubCode', () => {
  describe('when the code is valid', () => {
    it('should return the show sub type', () => {
      // given
      const code = 100
      const subCode = 101

      // when
      const showSubType = selectShowSubTypeByCodeAndSubCode(state, String(code), String(subCode))

      // then
      expect(showSubType.code).toStrictEqual(subCode)
    })
  })

  describe('when the code is not valid', () => {
    it('should return undefined', () => {
      // given
      const code = 100
      const subCode = 666

      // when
      const showSubType = selectShowSubTypeByCodeAndSubCode(state, String(code), String(subCode))

      // then
      expect(showSubType).toBeUndefined()
    })
  })
})
