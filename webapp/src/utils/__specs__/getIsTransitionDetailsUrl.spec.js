import getIsTransitionDetailsUrl from '../getIsTransitionDetailsUrl'

describe('src | helpers | getIsTransitionDetailsUrl', () => {
  describe('when we are o details url', () => {
    it('should return false', () => {
      // given
      const match = {
        params: {
          details: 'details',
        },
      }

      // when
      const isTransitionDetails = getIsTransitionDetailsUrl(match)

      //then
      expect(isTransitionDetails).toBe(false)
    })
  })

  describe('when we see transition in url', () => {
    it('should return true', () => {
      // given
      const match = {
        params: {
          details: 'transition',
        },
      }

      // when
      const isTransitionDetails = getIsTransitionDetailsUrl(match)

      //then
      expect(isTransitionDetails).toBe(true)
    })
  })
})
