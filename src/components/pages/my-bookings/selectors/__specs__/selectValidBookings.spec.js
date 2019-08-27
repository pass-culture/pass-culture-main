import { getIsNotAnActivationOffer, selectValidBookings } from '../selectValidBookings'

describe('src | components | pages | my-bookings | selectors | selectValidBookings', () => {
  describe('getIsNotAnActivationOffer()', () => {
    it('should be false when it is a offer without offer', () => {
      // given
      const offer = {}

      // when
      const result = getIsNotAnActivationOffer(offer)

      // then
      const expected = false
      expect(result).toStrictEqual(expected)
    })

    it('should be false when it is not an activation type', () => {
      // given
      const offer = {
        type: 'EventType.ANY',
      }

      // when
      const result = getIsNotAnActivationOffer(offer)

      // then
      const expected = true
      expect(result).toStrictEqual(expected)
    })

    it('should be false when it is an activation type (event)', () => {
      // given
      const offer = {
        type: 'EventType.ACTIVATION',
      }

      // when
      const result = getIsNotAnActivationOffer(offer)

      // then
      const expected = false
      expect(result).toStrictEqual(expected)
    })

    it('should be false when it is an activation type (thing)', () => {
      // given
      const offer = {
        type: 'ThingType.ACTIVATION',
      }

      // when
      const result = getIsNotAnActivationOffer(offer)

      // then
      const expected = false
      expect(result).toStrictEqual(expected)
    })
  })

  describe('selectValidBookings()', () => {
    it('should return valid bookings', () => {
      // given
      const state = {
        data: {
          bookings: [
            {
              id: 'b1',
              stockId: 's1',
            },
            {
              id: 'b2',
              stockId: 's2',
            },
          ],
          offers: [
            {
              id: 'o1',
              type: 'ThingType.MUSIQUE',
            },
            {
              id: 'o2',
              type: 'ThingType.MUSIQUE',
            },
          ],
          stocks: [
            {
              id: 's1',
              offerId: 'o1',
            },
            {
              id: 's2',
              offerId: 'o3',
            },
          ],
        },
      }

      // when
      const results = selectValidBookings(state)

      // then
      expect(results).toStrictEqual([{ id: 'b1', stockId: 's1' }])
    })
  })
})
