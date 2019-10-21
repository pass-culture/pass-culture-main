import React from 'react'

import { getCancellingUrl, mapDispatchToProps, mapStateToProps } from '../CancellingActionContainer'

describe('src | components | layout | Verso | VersoControls | booking | CancellingAction | CancellingActionContainer', () => {
  describe('getcancellingUrl', () => {
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
    it('should return an object with booking, cancelling link, offer and price', () => {
      // given
      const state = {
        data: {
          bookings: [{ id: 'AE' }],
          offers: [{ id: 'BF' }],
          stocks: [{ offerId: 'BF', price: 20 }],
        },
      }
      const ownProps = {
        location: {
          pathname: '/reservations/details/GM',
          search: '',
        },
        match: {
          params: {
            bookingId: 'AE',
          },
        },
      }

      // when
      const props = mapStateToProps(state, ownProps)

      // then
      expect(props).toStrictEqual({
        booking: { id: 'AE' },
        cancellingUrl: '/reservations/details/GM/reservation/annulation',
        offer: { id: 'BF' },
        price: 20,
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
      expect(dispatch.mock.calls[0][0]).toStrictEqual({
        options: {
          buttons: [
            <button
              className="popin-button"
              key="Oui"
              onClick={expect.any(Function)}
              type="button"
            >
              {'Oui'}
            </button>,
            <button
              className="popin-button"
              key="Non"
              onClick={expect.any(Function)}
              type="button"
            >
              {'Non'}
            </button>,
          ],
          handleClose: expect.any(Function),
          title: 'Offer title',
          text: 'Souhaitez-vous réellement annuler cette réservation ?',
        },
        type: 'TOGGLE_SHARE_POPIN',
      })
    })
  })
})
