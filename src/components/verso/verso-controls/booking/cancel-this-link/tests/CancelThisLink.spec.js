import React from 'react'
import { mount, shallow } from 'enzyme'
import { Router } from 'react-router-dom'
import { createBrowserHistory } from 'history'

import CancelThisLink from '../CancelThisLink'
import Price from '../../../../../layout/Price'

describe('src | components | verso | verso-controls | booking | CancelThisLink', () => {
  let props
  let dispatch
  let push

  beforeEach(() => {
    dispatch = jest.fn()
    push = jest.fn()
    props = {
      booking: {
        id: 'AAA',
        recommendation: {
          offerId: 'BBB',
        },
      },
      dispatch,
      history: {
        push,
      },
      isCancelled: false,
      priceValue: 42,
    }
  })

  describe('snapshot with required props', () => {
    it('should match snapshot', () => {
      // when
      const wrapper = shallow(<CancelThisLink {...props} />)

      // then
      expect(wrapper).toBeDefined()
      expect(wrapper).toMatchSnapshot()
    })
  })

  describe('render', () => {
    it('should display Price component, check icon, and label Annuler', () => {
      // when
      const wrapper = shallow(<CancelThisLink {...props} />)

      // then
      const price = wrapper.find(Price)
      const icon = wrapper.find('.icon-ico-check')
      const cancelLabel = wrapper.find('.pc-ticket-button-label')
      expect(icon).toHaveLength(1)
      expect(price).toHaveLength(1)
      expect(cancelLabel).toHaveLength(1)
      expect(cancelLabel.text()).toBe('Annuler')
    })

    it('should not contains a check icon when booking is cancelled', () => {
      // given
      props.isCancelled = true

      // when
      const wrapper = shallow(<CancelThisLink {...props} />)
      const icon = wrapper.find('.icon-ico-check')

      // then
      expect(icon).toHaveLength(0)
    })

    it('should open cancel popin when click on cancel button', () => {
      // given
      const history = createBrowserHistory()
      props.booking = {
        isUserCancellable: true,
        stock: {
          resolvedOffer: {
            name: 'foo',
          },
        },
      }
      const anyFunction = expect.any(Function)
      const expectedOptions = {
        options: {
          buttons: [
            <button
              className="no-border no-background no-outline is-block py12 is-bold fs14"
              id="popin-cancel-booking-yes"
              key="Oui"
              onClick={anyFunction}
              type="button"
            >
              <span>{'Oui'}</span>
            </button>,
            <button
              className="no-border no-background no-outline is-block py12 is-bold fs14"
              id="popin-cancel-booking-no"
              key="Non"
              onClick={anyFunction}
              type="button"
            >
              <span>{'Non'}</span>
            </button>,
          ],
          text: 'Souhaitez-vous réellement annuler cette réservation ?',
          title: 'foo',
        },
        type: 'TOGGLE_SHARE_POPIN',
      }
      const wrapper = mount(
        <Router history={history}>
          <CancelThisLink {...props} />
        </Router>
      )
      const cancelPopin = wrapper.find('#verso-cancel-booking-button')

      // when
      cancelPopin.simulate('click')

      // then
      expect(dispatch).toHaveBeenCalled()
      expect(dispatch.mock.calls[0][0]).toStrictEqual(expectedOptions)
    })
  })

  describe('onSuccess', () => {
    it('should redirect to cancelled booking page', () => {
      // given
      const wrapper = shallow(<CancelThisLink {...props} />)

      // when
      wrapper.instance().onSuccess(props.booking)

      // then
      expect(dispatch).toHaveBeenCalledWith({
        options: false,
        type: 'TOGGLE_SHARE_POPIN',
      })
      expect(push).toHaveBeenCalledWith('/decouverte/BBB/booking/AAA/cancelled')
    })
  })

  describe('onFailure', () => {
    it('should notify user with a failing message', () => {
      // given
      const state = {}
      const request = {}
      const wrapper = shallow(<CancelThisLink {...props} />)

      // when
      wrapper.instance().onFailure(state, request)

      // then
      expect(dispatch).toHaveBeenCalledWith({
        options: {
          buttons: expect.any(Array),
          text: "Une erreur inconnue s'est produite",
          title: 'Annulation impossible',
        },
        type: 'TOGGLE_SHARE_POPIN',
      })
    })
  })
})
