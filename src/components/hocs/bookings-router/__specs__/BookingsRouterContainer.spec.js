import { mapStateToProps } from '../BookingsRouterContainer'

describe('bookingsRouterContainer', () => {
  describe('when Bookings v2 feature is active', () => {
    it('should load Bookings v2', () => {
      // given
      const state = {
        data: {
          features: [
            {
              isActive: true,
              nameKey: 'BOOKINGS_V2',
            },
          ],
        },
      }

      // when
      const props = mapStateToProps(state)

      // then
      expect(props).toStrictEqual({
        isBookingsV2Active: true,
      })
    })
  })

  describe('when Bookings v2 feature is not active', () => {
    it('should load Bookings (v1)', () => {
      // given
      const state = {
        data: {
          features: [
            {
              isActive: false,
              nameKey: 'BOOKINGS_V2',
            },
          ],
        },
      }

      // when
      const props = mapStateToProps(state)

      // then
      expect(props).toStrictEqual({
        isBookingsV2Active: false,
      })
    })
  })
})
