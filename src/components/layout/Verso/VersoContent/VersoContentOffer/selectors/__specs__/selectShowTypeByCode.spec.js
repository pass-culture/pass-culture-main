import showTypes from './showTypes'
import selectShowTypeByCode from '../selectShowTypeByCode'

const state = { data: { showTypes } }

describe('src | components | verso | verso-content | verso-content-offer | selectors', () => {
  describe('selectShowTypeByCode', () => {
    it('find the show type with the good code', () => {
      // given
      const code = 100

      // when
      const showType = selectShowTypeByCode(state, String(code))

      // then
      expect(showType.code).toStrictEqual(code)
    })

    it('does not find any show type', () => {
      // given
      const code = 666

      // when
      const showType = selectShowTypeByCode(state, String(code))

      // then
      expect(showType).toStrictEqual(undefined)
    })
  })
})
