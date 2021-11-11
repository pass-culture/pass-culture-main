import musicTypes from './musicTypes'
import selectMusicTypeByCode from '../selectMusicTypeByCode'

const state = { data: { musicTypes } }

describe('src | components | layout | Verso | VersoContent | VersoContentOffer | selectors | selectMusicTypeByCode', () => {
  describe('when the code is valid', () => {
    it('should return the show sub type', () => {
      // given
      const code = 501

      // when
      const musicType = selectMusicTypeByCode(state, String(code))

      // then
      expect(musicType.code).toStrictEqual(code)
    })
  })

  describe('when the code is not valid', () => {
    it('should return undefined', () => {
      // given
      const code = 666

      // when
      const musicType = selectMusicTypeByCode(state, String(code))

      // then
      expect(musicType).toBeUndefined()
    })
  })
})
