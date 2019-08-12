import getIsFinished from '../getIsFinished'

describe('src | helpers | getIsFinished', () => {
  describe('getIsFinished', () => {
    it('should return false when no recommendation', () => {
      // when
      const result = getIsFinished(null)

      // then
      expect(result).toBe(false)
    })

    it('should return false when no mediation', () => {
      // given
      const offer = { isFinished: false }

      // when
      const result = getIsFinished(offer)

      // then
      expect(result).toBe(false)
    })

    it('should return false when offerId is tuto', () => {
      // given
      const offer = {}
      const mediation = { tutoIndex: 1 }

      // when
      const result = getIsFinished(offer, mediation)

      // then
      expect(result).toBe(false)
    })

    it('should return false when offer is not finished', () => {
      // given
      const offer = {
        isFinished: false,
      }
      const mediation = {}

      // when
      const result = getIsFinished(offer, mediation)

      // then
      expect(result).toBe(false)
    })

    it('should return true when offer is finished', () => {
      // given
      const offer = {
        isFinished: true,
      }
      const mediation = {}

      // when
      const result = getIsFinished(offer, mediation)

      // then
      expect(result).toBe(true)
    })
  })
})
