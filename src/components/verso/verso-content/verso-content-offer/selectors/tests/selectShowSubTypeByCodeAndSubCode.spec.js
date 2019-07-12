import showTypes from './showTypes'
import selectShowSubTypeByCodeAndSubCode from '../selectShowSubTypeByCodeAndSubCode'

const state = { data: { showTypes } }

describe('src | components | verso | verso-content | verso-content-offer | selectors', () => {
  describe('selectShowSubTypeByCodeAndSubCode', () => {
    it('find the show sub type with the good code', () => {
      // given
      const code = 100
      const subCode = 101

      // when
      const showSubType = selectShowSubTypeByCodeAndSubCode(state, String(code), String(subCode))

      // then
      expect(showSubType.code).toStrictEqual(subCode)
    })

    it('does not find any show sub type', () => {
      // given
      const code = 100
      const subCode = 666

      // when
      const showSubType = selectShowSubTypeByCodeAndSubCode(state, String(code), String(subCode))

      // then
      expect(showSubType).toStrictEqual(undefined)
    })
  })
})
