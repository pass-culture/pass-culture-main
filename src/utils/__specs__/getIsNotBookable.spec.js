import getIsNotBookable from '../getIsNotBookable'

describe('src | helpers | getIsNotBookable', () => {
  describe('getIsNotBookable', () => {
    it('should return false when no recommendation', () => {
      // when
      const result = getIsNotBookable(null)

      // then
      expect(result).toBe(false)
    })

    it('should return false when no mediation', () => {
      // given
      const offer = { isNotBookable: false }

      // when
      const result = getIsNotBookable(offer)

      // then
      expect(result).toBe(false)
    })

    it('should return false when offerId is tuto', () => {
      // given
      const offer = {}
      const mediation = { tutoIndex: 1 }

      // when
      const result = getIsNotBookable(offer, mediation)

      // then
      expect(result).toBe(false)
    })

    it('should return false when offer is not finished', () => {
      // given
      const offer = {
        isNotBookable: false,
      }
      const mediation = {}

      // when
      const result = getIsNotBookable(offer, mediation)

      // then
      expect(result).toBe(false)
    })

    it('should return true when offer is finished', () => {
      // given
      const offer = {
        isNotBookable: true,
      }
      const mediation = {}

      // when
      const result = getIsNotBookable(offer, mediation)

      // then
      expect(result).toBe(true)
    })
  })
})
