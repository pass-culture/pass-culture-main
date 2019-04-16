import React from 'react'
import { mount, shallow } from 'enzyme'
import { Router } from 'react-router'
import { Link } from 'react-router-dom'
import { createBrowserHistory } from 'history'
import Finishable from '../../../../layout/Finishable'
import BookThisButtonContainer from '../../book-this-button/BookThisButtonContainer'

import VersoBookingButton from '../VersoBookingButton'

describe('src | components | verso | VersoBookingButton', () => {
  describe('snapshot', () => {
    it('should match snapshot', () => {
      // given
      const props = {
        dispatch: jest.fn(),
        history: {},
        locationSearch: '',
      }

      // when
      const wrapper = shallow(<VersoBookingButton {...props} />)

      // then
      expect(wrapper).toBeDefined()
      expect(wrapper).toMatchSnapshot()
    })
  })

  describe('when offline', () => {
    it('should open cancel popin when click on cancel button', () => {
      // given
      const history = createBrowserHistory()
      const dispatch = jest.fn()
      const booking = {
        isUserCancellable: true,
        stock: {
          resolvedOffer: {
            eventOrThing: {
              name: 'foo',
            },
          },
        },
      }
      const props = {
        booking,
        dispatch,
        history,
        locationSearch: '',
        onlineOfferUrl: null,
      }
      const anyFunction = expect.any(Function)
      const expectedOptions = {
        options: {
          buttons: [
            <button
              className="no-border no-background no-outline is-block py12 is-bold fs14"
              key="Oui"
              onClick={anyFunction}
              type="button"
            >
              <span>Oui</span>
            </button>,
            <button
              className="no-border no-background no-outline is-block py12 is-bold fs14"
              key="Non"
              onClick={anyFunction}
              type="button"
            >
              <span>Non</span>
            </button>,
          ],
          text: 'Souhaitez-vous réellement annuler cette réservation ?',
          title: 'foo',
        },
        type: 'TOGGLE_SHARE_POPIN',
      }
      const wrapper = mount(
        <Router history={history}>
          <VersoBookingButton {...props} />
        </Router>
      )
      const cancelPopin = wrapper.find('#verso-cancel-booking-button')

      // when
      cancelPopin.simulate('click')

      // then
      expect(dispatch).toHaveBeenCalled()
      expect(dispatch.mock.calls[0][0]).toStrictEqual(expectedOptions)
    })

    it('should display a link to bookings when offer is not cancelable', () => {
      // given
      const history = createBrowserHistory()
      const dispatch = jest.fn()
      const booking = {
        isUserCancellable: false,
        stock: {
          resolvedOffer: {
            eventOrThing: {
              name: 'foo',
            },
          },
        },
      }
      const props = {
        booking,
        dispatch,
        history,
        locationSearch: '',
        onlineOfferUrl: null,
      }
      const wrapper = mount(
        <Router history={history}>
          <VersoBookingButton {...props} />
        </Router>
      )

      // when
      const linkComponent = wrapper.find(Link)

      // then
      expect(linkComponent).toBeDefined()
      expect(linkComponent.prop('id')).toBe('verso-already-booked-button')
      expect(linkComponent.prop('to')).toBe('/reservations')
      expect(linkComponent.prop('className')).toBe(
        'button is-primary is-medium'
      )
    })
  })

  describe('when online', () => {
    it('should render a link to access the offer', () => {
      // given
      const history = createBrowserHistory()
      const dispatch = jest.fn()
      const booking = {
        isUserCancellable: true,
        stock: {
          resolvedOffer: {
            eventOrThing: {
              name: 'foo',
            },
          },
        },
      }
      const props = {
        booking,
        dispatch,
        history,
        locationSearch: '',
        onlineOfferUrl: 'fake online url',
      }

      // when
      const wrapper = mount(
        <Router history={history}>
          <VersoBookingButton {...props} />
        </Router>
      )

      // then
      const link = wrapper.find('a')
      expect(link).toBeDefined()
      expect(link.prop('id')).toBe('verso-online-booked-button')
      expect(link.prop('href')).toBe(props.onlineOfferUrl)
      expect(link.prop('target')).toBe('_blank')
      expect(link.prop('rel')).toBe('noopener noreferrer')
      expect(link.prop('className')).toBe('button is-primary is-medium')
    })
  })

  describe('when no booking', () => {
    it('should render a booking button', () => {
      // given
      const history = createBrowserHistory()
      const dispatch = jest.fn()
      const booking = null
      const props = {
        booking,
        dispatch,
        history,
        locationSearch: '',
        onlineOfferUrl: 'fake online url',
      }

      // when
      const wrapper = shallow(<VersoBookingButton {...props} />)

      // then
      const finishableComponent = wrapper.find(Finishable)
      const bookThisButtonContainerComponent = wrapper.find(
        BookThisButtonContainer
      )
      expect(finishableComponent).toBeDefined()
      expect(bookThisButtonContainerComponent).toBeDefined()
      expect(finishableComponent.prop('finished')).toBe(false)
    })
  })
})
