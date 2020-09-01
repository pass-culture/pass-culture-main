import { findThumbByBookingId, findThumbByOfferId, mapStateToProps } from '../RectoContainer'

jest.mock('../../../../utils/thumb', () => ({
  DEFAULT_THUMB_URL: '/default/thumb/url',
}))

describe('components | RectoContainer', () => {
  describe('mapStateToProps', () => {
    it('should return mediation when booking id is provided and booking has a mediation', () => {
      // given
      const props = {
        match: {
          params: {
            bookingId: 'AB',
          },
        },
      }
      const state = {
        data: {
          bookings: [{ id: 'AB', stockId: 'AC' }],
          mediations: [{ id: 'AE', offerId: 'AD' }],
          offers: [{ id: 'AD', product: {}, thumbUrl: '/url-to-image/from-booking' }],
          stocks: [{ id: 'AC', offerId: 'AD' }],
        },
      }

      // when
      const result = mapStateToProps(state, props)

      // then
      expect(result).toStrictEqual({
        thumbUrl: '/url-to-image/from-booking',
      })
    })

    it('should return recommendation thumbUrl when offer id is provided and offer has a mediation', () => {
      // given
      const props = {
        match: {
          params: {
            offerId: 'AD',
          },
        },
        recommendation: { thumbUrl: '/url-to-image' },
      }
      const state = {
        data: {
          bookings: [{ id: 'AB', stockId: 'AC' }],
          mediations: [{ id: 'AE', offerId: 'AD' }],
          offers: [{ id: 'AD' }],
          stocks: [{ id: 'AC', offerId: 'AD' }],
        },
      }

      // when
      const result = mapStateToProps(state, props)

      // then
      expect(result).toStrictEqual({
        thumbUrl: '/url-to-image',
      })
    })
  })

  describe('findThumbByBookingId', () => {
    it('should return front text from mediation & thumb url from booking when booking has a mediation', () => {
      // given
      const match = {
        params: {
          bookingId: 'AB',
        },
      }
      const state = {
        data: {
          bookings: [{ id: 'AB', stockId: 'AC' }],
          mediations: [{ id: 'AE', offerId: 'AD', thumbUrl: '/url-to-image' }],
          offers: [{ id: 'AD', product: {}, thumbUrl: '/url-to-image/from-booking' }],
          stocks: [{ id: 'AC', offerId: 'AD' }],
        },
      }

      // when
      const result = findThumbByBookingId(state, match.params.bookingId, match)

      // then
      expect(result).toStrictEqual({
        thumbUrl: '/url-to-image/from-booking',
      })
    })

    it('should return no front text & thumb url from booking when booking has no mediation', () => {
      // given
      const match = {
        params: {
          bookingId: 'AB',
        },
      }
      const state = {
        data: {
          bookings: [{ id: 'AB', stockId: 'AC' }],
          mediations: [],
          offers: [
            {
              id: 'AD',
              product: { id: 'AE', thumbUrl: '/url-to-image/from-product' },
              thumbUrl: '/url-to-image/from-booking',
            },
          ],
          stocks: [{ id: 'AC', offerId: 'AD' }],
        },
      }

      // when
      const result = findThumbByBookingId(state, match.params.bookingId, match)

      // then
      expect(result).toStrictEqual({
        thumbUrl: '/url-to-image/from-booking',
      })
    })

    it('should return default thumb when there is no thumb on booking', () => {
      // given
      const match = {
        params: {
          bookingId: 'AB',
        },
      }
      const state = {
        data: {
          bookings: [{ id: 'AB', stockId: 'AC', thumbUrl: null }],
          mediations: [],
          offers: [{ id: 'AD', product: { id: 'AE', thumbUrl: '/url-to-image/from-product' } }],
          stocks: [{ id: 'AC', offerId: 'AD' }],
        },
      }

      // when
      const result = findThumbByBookingId(state, match.params.bookingId, match)

      // then
      expect(result).toStrictEqual({
        thumbUrl: '/default/thumb/url',
      })
    })
  })

  describe('findThumbByOfferId', () => {
    it('should return front text from mediation and thumb url from recommendation when offer has a mediation and a recommendation', () => {
      // given
      const match = {
        params: {
          offerId: 'AD',
        },
      }

      const recommendation = {
        thumbUrl: '/url-to-image',
      }

      const state = {
        data: {
          bookings: [],
          mediations: [{ id: 'AE', offerId: 'AD' }],
          offers: [{ id: 'AD', product: {} }],
          stocks: [{ id: 'AC', offerId: 'AD' }],
        },
      }

      // when
      const result = findThumbByOfferId(state, match.params.offerId, match, recommendation)

      // then
      expect(result).toStrictEqual({
        thumbUrl: '/url-to-image',
      })
    })

    it('should return no front text and use thumb url from offer when offer has no mediation', () => {
      // given
      const match = {
        params: {
          offerId: 'AD',
        },
      }

      const recommendation = undefined

      const state = {
        data: {
          bookings: [],
          mediations: [],
          offers: [{ id: 'AD', thumbUrl: '/url-to-image-from-offer' }],
          stocks: [{ id: 'AC', offerId: 'AD' }],
        },
      }

      // when
      const result = findThumbByOfferId(state, match.params.offerId, match, recommendation)

      // then
      expect(result).toStrictEqual({
        thumbUrl: '/url-to-image-from-offer',
      })
    })

    it('should use default thumb url when no mediation and offer has no thumb url', () => {
      // given
      const match = {
        params: {
          offerId: 'AD',
        },
      }

      const recommendation = undefined

      const state = {
        data: {
          bookings: [],
          mediations: [],
          offers: [{ id: 'AD', thumbUrl: null }],
          stocks: [{ id: 'AC', offerId: 'AD' }],
        },
      }

      // when
      const result = findThumbByOfferId(state, match.params.offerId, match, recommendation)

      // then
      expect(result).toStrictEqual({
        thumbUrl: '/default/thumb/url',
      })
    })
  })
})
