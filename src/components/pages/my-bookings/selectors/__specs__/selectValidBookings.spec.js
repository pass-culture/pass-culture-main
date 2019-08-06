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
              stock: {
                offerId: 'MEFA',
              },
            },
            {
              stock: {
                offerId: 'TATA',
              },
            },
          ],
          offers: [
            {
              id: 'MEFA',
              type: 'ThingType.MUSIQUE',
            },
            {
              id: 'TOTO',
              type: 'ThingType.MUSIQUE',
            },
          ],
        },
      }

      // when
      const results = selectValidBookings(state)

      // then
      expect(results).toStrictEqual([
        {
          stock: {
            offerId: 'MEFA',
          },
        },
        undefined,
      ])
    })
  })
})
