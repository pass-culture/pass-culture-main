import isOfferBookableForUser from '../getIsNotBookable'

describe('src | helpers | isOfferBookableForUser', () => {
  describe('isOfferBookableForUser', () => {
    it('should return false when no recommendation', () => {
      // when
      const result = isOfferBookableForUser(null)

      // then
      expect(result).toBe(false)
    })

    it('should return false when no mediation', () => {
      // given
      const offer = { isNotBookable: false }

      // when
      const result = isOfferBookableForUser(offer)

      // then
      expect(result).toBe(false)
    })

    it('should return false when offerId is tuto', () => {
      // given
      const offer = {}
      const mediation = { tutoIndex: 1 }

      // when
      const result = isOfferBookableForUser(offer, mediation)

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
      const result = isOfferBookableForUser(offer, mediation)

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
      const result = isOfferBookableForUser(offer, mediation)

      // then
      expect(result).toBe(true)
    })
  })
})
