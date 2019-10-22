import { mapStateToProps } from '../BookingFormContentContainer'

describe('src | components | layout | Booking | BookingForm | BookingFormContentContainer', () => {
  describe('mapStateToProps', () => {
    it('should return an object of props', () => {
      // given
      const state = {
        data: {
          features: [
            {
              nameKey: 'DUO_OFFER',
              isActive: true,
            },
          ],
          offers: [
            {
              id: 'O1',
              isDuo: true,
            },
          ],
          stocks: [
            {
              id: 'S1',
              offerId: 'O1',
              available: 3,
            },
          ],
        },
      }

      const ownProps = {
        offerId: 'O1',
        values: {
          stockId: 'S1',
        },
      }

      // when
      const props = mapStateToProps(state, ownProps)

      // then
      expect(props).toStrictEqual({
        isStockDuo: true,
      })
    })
  })
})
