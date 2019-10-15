import getStyle from '../getStyle'

describe('src | components | layout | Verso | VersoContent | VersoContentOffer | utils | getStyle', () => {
  describe('when it is a tuto', () => {
    it('should return empty string', () => {
      // given
      const state = {}
      const extraData = undefined

      // when
      const style = getStyle(state, extraData)

      // then
      expect(style).toBe('')
    })
  })

  describe('when it is an offer with no extra data', () => {
    it('should return empty string', () => {
      // given
      const state = {}
      const extraData = null

      // when
      const style = getStyle(state, extraData)

      // then
      expect(style).toBe('')
    })
  })

  describe('when the offer is of the music style', () => {
    it('should return this label and sub label', () => {
      // given
      const state = {
        data: {
          musicTypes: [
            {
              children: [
                {
                  code: 1,
                  label: 'Contenders',
                },
              ],
              code: 2,
              label: 'Rap',
            },
          ],
        },
      }
      const extraData = {
        musicSubType: '1',
        musicType: '2',
      }

      // when
      const style = getStyle(state, extraData)

      // then
      expect(style).toBe('Rap / Contenders')
    })
  })

  describe('when the offer is of the show style', () => {
    it('should return this label and sub label', () => {
      // given
      const state = {
        data: {
          showTypes: [
            {
              children: [
                {
                  code: 1,
                  label: 'Contenders',
                },
              ],
              code: 2,
              label: 'Rap',
            },
          ],
        },
      }
      const extraData = {
        showSubType: '1',
        showType: '2',
      }

      // when
      const style = getStyle(state, extraData)

      // then
      expect(style).toBe('Rap / Contenders')
    })
  })
})
