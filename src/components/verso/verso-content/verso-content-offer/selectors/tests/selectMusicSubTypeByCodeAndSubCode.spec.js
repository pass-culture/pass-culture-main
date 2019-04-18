import musicTypes from './musicTypes'
import selectMusicSubTypeByCodeAndSubCode from '../selectMusicSubTypeByCodeAndSubCode'

const state = { data: { musicTypes } }

describe('src | components | verso | verso-content | verso-content-offer | selectors', () => {
  describe('selectMusicSubTypeByCodeAndSubCode', () => {
    it('find the music sub type with the good code', () => {
      // given
      const code = 501
      const subCode = 519

      // when
      const musicSubType = selectMusicSubTypeByCodeAndSubCode(
        state,
        String(code),
        String(subCode)
      )

      // then
      expect(musicSubType.code).toEqual(subCode)
    })

    it('does not find any music sub type', () => {
      // given
      const code = 501
      const subCode = 666

      // when
      const musicSubType = selectMusicSubTypeByCodeAndSubCode(
        state,
        String(code),
        String(subCode)
      )

      // then
      expect(musicSubType).toEqual(undefined)
    })
  })
})
