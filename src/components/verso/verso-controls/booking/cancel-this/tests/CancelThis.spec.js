import React from 'react'
import { mount, shallow } from 'enzyme'
import { Router } from 'react-router-dom'
import { createBrowserHistory } from 'history'

import CancelThis from '../CancelThis'
import Price from '../../../../../layout/Price'

describe('src | components | verso | verso-controls | booking | CancelThis', () => {
  let props
  let dispatch

  beforeEach(() => {
    dispatch = jest.fn()
    props = {
      booking: {},
      dispatch,
      history: {},
      isCancelled: false,
      priceValue: 42,
    }
  })

  describe('snapshot with required props', () => {
    it('should match snapshot', () => {
      // when
      const wrapper = shallow(<CancelThis {...props} />)

      // then
      expect(wrapper).toBeDefined()
      expect(wrapper).toMatchSnapshot()
    })
  })

  describe('render', () => {
    it('should display Price component, check icon, and label Annuler', () => {
      // when
      const wrapper = shallow(<CancelThis {...props} />)
      const price = wrapper.find(Price)
      const icon = wrapper.find('.icon-ico-check')
      const cancelLabel = wrapper.find('.pc-ticket-button-label')

      // then
      expect(icon).toHaveLength(1)
      expect(price).toHaveLength(1)
      expect(cancelLabel).toHaveLength(1)
      expect(cancelLabel.text()).toBe('Annuler')
    })

    it('should not contains a check icon when booking is cancelled', () => {
      // given
      props.isCancelled = true

      // when
      const wrapper = shallow(<CancelThis {...props} />)
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
              key="Oui"
              id="popin-cancel-booking-yes"
              onClick={anyFunction}
              type="button"
            >
              <span>Oui</span>
            </button>,
            <button
              className="no-border no-background no-outline is-block py12 is-bold fs14"
              key="Non"
              id="popin-cancel-booking-no"
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
          <CancelThis {...props} />
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
})
