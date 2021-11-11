import musicTypes from './musicTypes'
import selectMusicSubTypeByCodeAndSubCode from '../selectMusicSubTypeByCodeAndSubCode'

const state = { data: { musicTypes } }

describe('src | components | layout | Verso | VersoContent | VersoContentOffer | selectors | selectMusicSubTypeByCodeAndSubCode', () => {
  describe('when the code is valid', () => {
    it('should return the music sub type', () => {
      // given
      const code = 501
      const subCode = 519

      // when
      const musicSubType = selectMusicSubTypeByCodeAndSubCode(state, String(code), String(subCode))

      // then
      expect(musicSubType.code).toBe(subCode)
    })
  })

  describe('when the code is not valid', () => {
    it('should return undefined', () => {
      // given
      const code = 501
      const subCode = 666

      // when
      const musicSubType = selectMusicSubTypeByCodeAndSubCode(state, String(code), String(subCode))

      // then
      expect(musicSubType).toBeUndefined()
    })
  })
})
