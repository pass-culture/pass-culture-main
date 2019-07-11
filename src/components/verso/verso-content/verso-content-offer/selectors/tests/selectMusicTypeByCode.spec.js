import musicTypes from './musicTypes'
import selectMusicTypeByCode from '../selectMusicTypeByCode'

const state = { data: { musicTypes } }

describe('src | components | verso | verso-content | verso-content-offer | selectors', () => {
  describe('selectMusicTypeByCode', () => {
    it('find the music type with the good code', () => {
      // given
      const code = 501

      // when
      const musicType = selectMusicTypeByCode(state, String(code))

      // then
      expect(musicType.code).toStrictEqual(code)
    })

    it('does not find any music type', () => {
      // given
      const code = 666

      // when
      const musicType = selectMusicTypeByCode(state, String(code))

      // then
      expect(musicType).toStrictEqual(undefined)
    })
  })
})
