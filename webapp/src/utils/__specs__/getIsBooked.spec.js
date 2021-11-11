import getIsBooked from '../getIsBooked'

describe('src | helpers | getIsBooked', () => {
  describe('when my booking is not cancelled', () => {
    it('should return true', () => {
      // given
      const booking = {
        isCancelled: false,
      }

      // when
      const isBooked = getIsBooked(booking)

      //then
      expect(isBooked).toBe(true)
    })
  })

  describe('when my booking is cancelled', () => {
    it('should return false', () => {
      // given
      const booking = {
        isCancelled: true,
      }

      // when
      const isBooked = getIsBooked(booking)

      //then
      expect(isBooked).toBe(false)
    })
  })
})
