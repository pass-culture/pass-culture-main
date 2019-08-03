import { mapStateToProps } from '../BookingItemContainer'

describe('src | components | pages | my-bookings | BookingItemContainer', () => {
  describe('mapStateToProps()', () => {
    it('should return props with date elements', () => {
      // given
      const bookingId = 'AE'
      const token = 'BBBB'
      const offerId = 'CCCC'
      const isCancelled = true
      const mediationId = 'AAAA'
      const departementCode = '93'
      const productName = 'Fake booking name'
      const beginningDatetime = '2019-05-15T20:00:00Z'
      const pathname = '/reservations'
      const search = ''
      const thumbUrl = 'https://example.net/mediation/image'
      const mediation = {
        id: mediationId,
      }
      const isFinished = false
      const offer = {
        id: offerId,
        isEvent: true,
        isFinished,
        product: { name: productName },
        venue: {
          departementCode,
        },
      }
      const recommendationId = 'AE'
      const recommendation = {
        id: recommendationId,
        mediationId,
        offerId,
        thumbUrl,
      }
      const state = {
        data: {
          mediations: [mediation],
          offers: [offer],
          recommendations: [recommendation],
        },
      }
      const ownProps = {
        booking: {
          id: bookingId,
          isCancelled,
          recommendationId,
          stock: {
            beginningDatetime,
            offerId,
          },
          token,
        },
        location: {
          pathname,
          search,
        },
      }

      // when
      const props = mapStateToProps(state, ownProps)

      // then
      const expected = {
        isFinished,
        mediation,
        offer,
        recommendation,
        ribbon: {
          label: 'Annulé',
          type: 'cancelled',
        },
      }
      expect(props).toStrictEqual(expected)
    })
  })
})
