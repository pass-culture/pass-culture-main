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
          bookings: [{ id: 'AB', stockId: 'AC', thumbUrl: '/url-to-image/from-booking' }],
          mediations: [{ frontText: 'super offre', id: 'AE', offerId: 'AD' }],
          offers: [{ id: 'AD', product: {} }],
          stocks: [{ id: 'AC', offerId: 'AD' }],
        },
      }

      // when
      const result = mapStateToProps(state, props)

      // then
      expect(result).toStrictEqual({
        frontText: 'super offre',
        thumbUrl: '/url-to-image/from-booking',
        withMediation: true,
      })
    })

    it('should return mediation when offer id is provided and offer has a mediation', () => {
      // given
      const props = {
        match: {
          params: {
            offerId: 'AD',
          },
        },
      }
      const state = {
        data: {
          bookings: [{ id: 'AB', stockId: 'AC' }],
          mediations: [
            { frontText: 'super offre', id: 'AE', offerId: 'AD', thumbUrl: '/url-to-image' },
          ],
          offers: [{ id: 'AD' }],
          stocks: [{ id: 'AC', offerId: 'AD' }],
        },
      }

      // when
      const result = mapStateToProps(state, props)

      // then
      expect(result).toStrictEqual({
        frontText: 'super offre',
        thumbUrl: '/url-to-image',
        withMediation: true,
      })
    })
  })

  describe('findThumbByBookingId', () => {
    it('should return no front text nor thumb url when bookingId is menu', () => {
      // given
      const match = {
        params: {
          bookingId: 'menu',
        },
      }
      const state = {
        data: {
          bookings: [{ id: 'AE' }],
        },
      }

      // when
      const result = findThumbByBookingId(state, match.params.bookingId, match)

      // then
      expect(result).toStrictEqual({
        frontText: '',
        thumbUrl: '',
        withMediation: false,
      })
    })

    it('should return front text from mediation & thumb url from bookling when booking has a mediation', () => {
      // given
      const match = {
        params: {
          bookingId: 'AB',
        },
      }
      const state = {
        data: {
          bookings: [{ id: 'AB', stockId: 'AC', thumbUrl: '/url-to-image/from-booking' }],
          mediations: [
            { frontText: 'super offre', id: 'AE', offerId: 'AD', thumbUrl: '/url-to-image' },
          ],
          offers: [{ id: 'AD', product: {} }],
          stocks: [{ id: 'AC', offerId: 'AD' }],
        },
      }

      // when
      const result = findThumbByBookingId(state, match.params.bookingId, match)

      // then
      expect(result).toStrictEqual({
        frontText: 'super offre',
        thumbUrl: '/url-to-image/from-booking',
        withMediation: true,
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
          bookings: [{ id: 'AB', stockId: 'AC', thumbUrl: '/url-to-image/from-booking' }],
          mediations: [],
          offers: [{ id: 'AD', product: { id: 'AE', thumbUrl: '/url-to-image/from-product' } }],
          stocks: [{ id: 'AC', offerId: 'AD' }],
        },
      }

      // when
      const result = findThumbByBookingId(state, match.params.bookingId, match)

      // then
      expect(result).toStrictEqual({
        frontText: '',
        thumbUrl: '/url-to-image/from-booking',
        withMediation: false,
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
        frontText: '',
        thumbUrl: '/default/thumb/url',
        withMediation: false,
      })
    })
  })

  describe('findThumbByOfferId', () => {
    it('should return front text & thumb url from mediation when offer has a mediation', () => {
      // given
      const match = {
        params: {
          offerId: 'AD',
        },
      }
      const state = {
        data: {
          bookings: [],
          mediations: [
            { frontText: 'super offre', id: 'AE', offerId: 'AD', thumbUrl: '/url-to-image' },
          ],
          offers: [{ id: 'AD', product: {} }],
          stocks: [{ id: 'AC', offerId: 'AD' }],
        },
      }

      // when
      const result = findThumbByOfferId(state, match.params.offerId, match)

      // then
      expect(result).toStrictEqual({
        frontText: 'super offre',
        thumbUrl: '/url-to-image',
        withMediation: true,
      })
    })

    it('should return no front text and use thumb url from product when offer has no mediation', () => {
      // given
      const match = {
        params: {
          offerId: 'AD',
        },
      }
      const state = {
        data: {
          bookings: [],
          mediations: [],
          offers: [{ id: 'AD', product: { id: 'AE', thumbUrl: '/url-to-image' } }],
          stocks: [{ id: 'AC', offerId: 'AD' }],
        },
      }

      // when
      const result = findThumbByOfferId(state, match.params.offerId, match)

      // then
      expect(result).toStrictEqual({
        frontText: '',
        thumbUrl: '/url-to-image',
        withMediation: false,
      })
    })
  })
})
