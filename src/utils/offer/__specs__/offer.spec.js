import { checkOfferCannotBeBooked } from '../offer'

describe('utils | offer', () => {
  describe('offerCannotBeBooked', () => {
    it('should return true when offer is not bookable and not fully booked', () => {
      // given
      const offer = {
        isFullyBooked: false,
        isNotBookable: true
      }

      // when
      const result = checkOfferCannotBeBooked(offer)

      // then
      expect(result).toBe(true)
    })

    it('should return true when offer is bookable and fully booked', () => {
      // given
      const offer = {
        isFullyBooked: true,
        isNotBookable: false
      }

      // when
      const result = checkOfferCannotBeBooked(offer)

      // then
      expect(result).toBe(true)
    })

    it('should return true when offer is not bookable and fully booked', () => {
      // given
      const offer = {
        isFullyBooked: true,
        isNotBookable: true
      }

      // when
      const result = checkOfferCannotBeBooked(offer)

      // then
      expect(result).toBe(true)
    })

    it('should return false when offer is bookable and not fully booked', () => {
      // given
      const offer = {
        isFullyBooked: false,
        isNotBookable: false
      }

      // when
      const result = checkOfferCannotBeBooked(offer)

      // then
      expect(result).toBe(false)
    })
  })
})
