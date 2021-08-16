import { mapStateToProps } from '../BookingFormContentContainer'

describe('src | components | BookingFormContentContainer', () => {
  describe('mapStateToProps', () => {
    it('should return an object of props', () => {
      // given
      const state = {
        data: {
          offers: [
            {
              id: 'O1',
              isDigital: true,
              isDuo: true,
              offerType: {
                canExpire: false,
              },
              subcategoryId: 'cinema',
              url: 'http://fake-url.com',
            },
          ],
          stocks: [
            {
              id: 'S1',
              offerId: 'O1',
              remainingQuantity: 3,
            },
          ],
          features: [{ nameKey: 'AUTO_ACTIVATE_DIGITAL_BOOKINGS', isActive: true }],
          categories: [
            {
              categories: [],
              subcategories: [{ id: 'cinema', canExpire: false }],
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
        canExpire: false,
        isDigital: true,
        isStockDuo: true,
        hasActivationCode: false,
      })
    })
  })
})
