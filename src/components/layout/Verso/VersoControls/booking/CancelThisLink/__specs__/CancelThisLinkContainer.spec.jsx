import React from 'react'

import { mapDispatchToProps, mapStateToProps } from '../CancelThisLinkContainer'

describe('src | components | layout | Verso | VersoControls | booking | CancelThisLinkContainer', () => {
  describe('mapStateToProps', () => {
    it('should map booking, isBookingFinished and offer', () => {
      // given
      const state = {
        data: {
          bookings: [{ id: 'AE' }],
          mediations: [{ id: 'AE' }],
          offers: [{ id: 'BF', isFinished: false }],
          stocks: [{ offerId: 'BF' }],
        },
      }
      const ownProps = {
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
        isBookingFinished: false,
        offer: { id: 'BF', isFinished: false },
        stock: { offerId: 'BF' },
      })
    })
  })

  describe('mapDispatchToProps', () => {
    let ownProps
    let dispatch
    let push

    beforeEach(() => {
      dispatch = jest.fn()
      push = jest.fn()
      ownProps = {
        booking: {
          id: 'AAA',
        },
        dispatch,
        history: {
          push,
        },
        isCancelled: false,
        isFinished: false,
        location: {},
        match: { params: {} },
        priceValue: 42,
        offer: {
          id: 'BBB',
          name: 'foo',
        },
      }
    })

    it('should open cancel popin when click on cancel button', () => {
      // given
      const bookingId = 'AE'
      const offerName = 'foo'
      ownProps = {
        location: {
          pathname: '',
        },
        match: {
          params: {},
        },
      }
      const anyFunction = expect.any(Function)
      const expectedOptions = {
        options: {
          buttons: [
            <button
              className="no-background py12 is-bold fs14"
              id="popin-cancel-booking-yes"
              key="Oui"
              onClick={anyFunction}
              type="button"
            >
              {'Oui'}
            </button>,
            <button
              className="no-background py12 is-bold fs14"
              id="popin-cancel-booking-no"
              key="Non"
              onClick={anyFunction}
              type="button"
            >
              {'Non'}
            </button>,
          ],
          offerName,
          text: 'Souhaitez-vous réellement annuler cette réservation ?',
        },
        type: 'TOGGLE_SHARE_POPIN',
      }

      // when
      mapDispatchToProps(dispatch, ownProps).openCancelPopin(bookingId, offerName)

      // then
      expect(dispatch.mock.calls[0][0]).toStrictEqual(expectedOptions)
    })
  })
})
