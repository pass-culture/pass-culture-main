// $(yarn bin)/jest --env=jsdom ./src/components/verso/verso-controls/booking/tests/CancelButton.spec.js --watch
import React from 'react'
import { mount, shallow } from 'enzyme'
import { Router } from 'react-router-dom'
import { createBrowserHistory } from 'history'

import CancelButton from '../CancelButton'
import Price from '../../../../layout/Price'

const defaultprops = {
  booking: {},
  dispatch: jest.fn(),
  history: {},
  isCancelled: false,
  locationSearch: '?astring',
  priceValue: 42,
}

describe('src | components | verso | verso-controls | booking | CancelButton', () => {
  describe('snapshot with required props', () => {
    it('should match snapshot', () => {
      // when
      const wrapper = shallow(<CancelButton {...defaultprops} />)

      // then
      expect(wrapper).toBeDefined()
      expect(wrapper).toMatchSnapshot()
    })
  })

  describe('render', () => {
    it('contains price, check-icon, label', () => {
      // when
      const wrapper = shallow(<CancelButton {...defaultprops} />)
      const price = wrapper.find(Price)
      const icon = wrapper.find('.icon-ico-check')
      const label = wrapper.find('.pc-ticket-button-label')

      // then
      expect(icon).toHaveLength(1)
      expect(price).toHaveLength(1)
      expect(label).toHaveLength(1)
    })

    it('do not contains check icon', () => {
      // given
      const props = { ...defaultprops, isCancelled: true }

      // when
      const wrapper = shallow(<CancelButton {...props} />)
      const icon = wrapper.find('.icon-ico-check')

      // then
      expect(icon).toHaveLength(0)
    })

    it('should open cancel popin when click on cancel button', () => {
      // given
      const history = createBrowserHistory()
      const dispatch = jest.fn()
      const booking = {
        isUserCancellable: true,
        stock: {
          resolvedOffer: {
            name: 'foo',
          },
        },
      }
      const props = {
        booking,
        dispatch,
        history,
        isCancelled: false,
        locationSearch: '',
        priceValue: [12],
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
          <CancelButton {...props} />
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
