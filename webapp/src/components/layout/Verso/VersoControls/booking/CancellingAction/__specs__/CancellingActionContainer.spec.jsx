import moment from 'moment'

import { getCancellingUrl, mapDispatchToProps, mapStateToProps } from '../CancellingActionContainer'

describe('verso | booking | CancellingActionContainer', () => {
  describe('getCancellingUrl', () => {
    describe('when I am in reservations page', () => {
      it('should return a URL without booking id', () => {
        // given
        const bookingId = 'MEFA'
        const params = {
          booking: undefined,
          bookingId: 'MEFA',
          cancellation: undefined,
        }
        const pathname = '/reservations/details/GM'
        const search = ''

        // when
        const url = getCancellingUrl(bookingId, params, pathname, search)

        // then
        expect(url).toBe('/reservations/details/GM/reservation/annulation')
      })
    })

    describe('when I am in an other page', () => {
      it('should return a URL with booking id', () => {
        // given
        const bookingId = 'MEFA'
        const params = {
          booking: undefined,
          bookingId: undefined,
          cancellation: undefined,
        }
        const pathname = '/reservations/details/GM'
        const search = ''

        // when
        const url = getCancellingUrl(bookingId, params, pathname, search)

        // then
        expect(url).toBe('/reservations/details/GM/reservation/MEFA/annulation')
      })
    })

    describe('when I am in an URL with keywords (search)', () => {
      it('should return a URL with booking id and keywords', () => {
        // given
        const bookingId = 'MEFA'
        const params = {
          booking: undefined,
          bookingId: undefined,
          cancellation: undefined,
        }
        const pathname = '/reservations/details/GM'
        const search = '?mots-cles=Théâtre'

        // when
        const url = getCancellingUrl(bookingId, params, pathname, search)

        // then
        expect(url).toBe('/reservations/details/GM/reservation/MEFA/annulation?mots-cles=Théâtre')
      })
    })
  })

  describe('mapStateToProps', () => {
    it('should return an object with booking, cancelling link, offer and price when offer is not duo and booking quantity is 1', () => {
      // given
      const state = {
        data: {
          offers: [{ id: 'BF', isDuo: false }],
          stocks: [{ id: 'CF', offerId: 'BF', price: 20, beginningDatetime: null }],
          bookings: [{ id: 'DF', stockId: 'CF', quantity: 1 }],
        },
      }
      const ownProps = {
        location: {
          pathname: '/reservations/details/GM',
          search: '',
        },
        match: {
          params: {
            bookingId: 'DF',
          },
        },
      }

      // when
      const props = mapStateToProps(state, ownProps)

      // then
      expect(props).toStrictEqual({
        booking: { id: 'DF', quantity: 1, stockId: 'CF' },
        cancellingUrl: '/reservations/details/GM/reservation/annulation',
        offer: { id: 'BF', isDuo: false },
        offerCanBeCancelled: true,
        price: 20,
      })
    })

    describe('when offer event is past', () => {
      it('should not be cancellable anymore', () => {
        // given
        const now = moment()
        const oneDayBeforeNow = now.subtract(1, 'days').format()

        const state = {
          data: {
            offers: [{ id: 'BF', isDuo: false }],
            stocks: [{ id: 'CF', offerId: 'BF', price: 20, beginningDatetime: oneDayBeforeNow }],
            bookings: [{ id: 'DF', stockId: 'CF', quantity: 1 }],
          },
        }
        const ownProps = {
          location: {
            pathname: '/reservations/details/GM',
            search: '',
          },
          match: {
            params: {
              bookingId: 'DF',
            },
          },
        }

        // when
        const props = mapStateToProps(state, ownProps)

        // then
        expect(props).toStrictEqual({
          booking: { id: 'DF', quantity: 1, stockId: 'CF' },
          cancellingUrl: '/reservations/details/GM/reservation/annulation',
          offer: { id: 'BF', isDuo: false },
          offerCanBeCancelled: false,
          price: 20,
        })
      })
    })
  })

  describe('mapDispatchToProps', () => {
    it('should open cancel popin when click on cancel button', () => {
      // given
      const dispatch = jest.fn()
      const ownProps = {
        history: {
          push: jest.fn(),
        },
        location: {
          pathname: '',
          search: '',
        },
      }
      const bookingId = 'ME'
      const offerName = 'Offer title'
      const offerId = 'FA'

      // when
      mapDispatchToProps(dispatch, ownProps).openCancelPopin(bookingId, offerName, offerId)

      // then
      expect(dispatch.mock.calls[0][0].options.buttons).toStrictEqual(expect.any(Array))
      expect(dispatch.mock.calls[0][0].options.handleClose).toStrictEqual(expect.any(Function))
      expect(dispatch.mock.calls[0][0].options.title).toBe('Offer title')
      expect(dispatch.mock.calls[0][0].options.text).toBe(
        'Souhaites-tu réellement annuler cette réservation ?'
      )
      expect(dispatch.mock.calls[0][0].type).toBe('TOGGLE_SHARE_POPIN')
    })
  })
})
